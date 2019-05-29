---
layout: summary
title: 并行编程-MPI
---

消息传递模型在上个世纪90年代十分盛行，通常主进程(master process)通过对从进程(slave process)发送一个描述工作的消息来把这个工作分配给它。由于当时很多软件库都采用了这个模型，但由于不同软件定义上的区别存在大量差异，故在SC'92上制定了消息传递接口(Message Passing Interface, MPI)的标准。过了两年一个完整的接口定义(MPI-1)就已经被实现出来，这是MPI的前身

## 基本概念
* 通信子(communicator)：通信子定义了一组能够互相发消息的进程。在这组进程中，每个进程会被分配一个序号，称作秩(rank)，进程间显性地通过指定秩来进行通信。通信的基础建立在不同进程间发送和接收操作。一个进程可以通过指定另一个进程的秩以及一个独一无二的消息标签(tag)来发送消息给另一个进程。
* 点对点(point-to-point)通信：一个发送者、一个接受者。
* 集体性(collective)通信：某个进程跟其他所有进程通信

## 常用API
* `MPI_Init(int* argc,char*** argv)`
* `MPI_Comm_size(MPI_Comm communicator,int* size)`：确定进程数目，通信子通常用`MPI_COMM_WORLD`取代，其中包含了当前MPI任务中所有进程
* `MPI_Comm_rank(MPI_Comm communicator,int* rank)`：确定调用进程的标号，从0开始
* `MPI_Finalize()`
* `int MPI_Test(MPI_Request *request, int *flag, MPI_Status *status)`：测试消息是否收到
* `int MPI_Wait(MPI_Request *request, MPI_Status *status)`

```cpp
#include <mpi.h>

int main(int argc, char* argv[])
{
    int npes, myrank;
    MPI_Init(&argc, &argv);
    MPI_Comm_size(MPI_COMM_WORLD, &npes);
    MPI_Comm_rank(MPI_COMM_WORLD, &myrank);
    printf("From process %d out of %d, Hello World!\n", myrank, npes);
    MPI_Finalize();
}
```

## 编译指令
* `<mpi.h>`
* `mpicc`、`mpic++`：mpicc二进制程序其实只是对gcc做了一层封装，使得编译和链接MPI程序更加方便
* `mpirun -np 2 foo : -np 4 bar`
* `--hostfile`、`--host`：确定主机

程序编译好后就可以被执行了。不过执行之前还需要一些额外配置，如果要在好几个节点的集群上面跑MPI，则需要配置一个host文件；单机则不需要。

需要配置的host文件会包含你想要运行的所有节点的名称。为了运行方便，需要确认所有这些节点之间能通过SSH通信，并且需要根据[设置认证文件](http://www.eng.cam.ac.uk/help/jpmg/ssh/authorized_keys_howto.html)这个教程配置不需要密码的SSH访问。举例host文件如下：

```bash
$ cat host_file
cetus1:2
cetus2:2
cetus3
cetus4
$ export MPI_HOSTS=host_file
```

冒号后面跟的数字代表先在本机上创建这么多进程，然后再去其他机器上创建。

## 点对点通信
一个关键在于要**重叠通信和计算**
* `int MPI_Send(void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm)`
* `int MPI_Recv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Status *status)`
* `int MPI_Isend(void *buf, int count, MPI_Datatype datatype, int dest, int tag, MPI_Comm comm,
MPI_Request *request)`
* `int MPI_Irecv(void *buf, int count, MPI_Datatype datatype, int source, int tag, MPI_Comm comm, MPI_Request *request)`

MPI的发送模式
* `MPI_Send`/`MPI_Isend`：标准模式（阻塞/非阻塞），直到使用发送缓冲才返回
* `MPI_Bsend`/`MPI_Ibsend`：缓冲模式，立即返回，可以使用发送缓冲
    - 相关操作：`MPI_buffer_attach`、`MPI_buffer_detach`
* `MPI_Ssend`/`MPI_Issend`：同步模式，不会返回直到收到posted
* `MPI_Rsend`/`MPI_Irsend`：只有在matching receive已经就绪时才使用

```cpp
MPI_Send(
    void* data,
    int count,
    MPI_Datatype datatype,
    int destination,
    int tag,
    MPI_Comm communicator)

MPI_Recv(
    void* data,
    int count,
    MPI_Datatype datatype,
    int source,
    int tag,
    MPI_Comm communicator,
    MPI_Status* status)

typedef struct MPI_Status {
    int MPI_SOURCE;
    int MPI_TAG;
    int MPI_ERROR;
};
```

第一个参数是数据缓存。第二个和第三个参数分别描述了数据的数量和类型。`MPI_send`会精确地发送`count`指定的数量个元素，`MPI_Recv`会最多接受`count` 个元素（之后会详细讲）。第四个和第五个参数指定了发送方/接受方进程的秩以及信息的标签。第六个参数指定了使用的`communicator`。`MPI_Recv`方法特有的最后一个参数提供了接受到的信息的状态。

```cpp
// 得到当前进程的 rank 以及整个 communicator 的大小
int world_rank;
MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
int world_size;
MPI_Comm_size(MPI_COMM_WORLD, &world_size);

int number;
if (world_rank == 0) {
    number = -1;
    MPI_Send(&number, 1, MPI_INT, 1, 0, MPI_COMM_WORLD);
} else if (world_rank == 1) {
    MPI_Recv(&number, 1, MPI_INT, 0, 0, MPI_COMM_WORLD,
             MPI_STATUS_IGNORE);
    printf("Process 1 received number %d from process 0\n",
           number);
}
```

## 群组通信
![boardcast](https://mpitutorial.com/tutorials/mpi-broadcast-and-collective-communication/broadcast_pattern.png)

```cpp
MPI_Bcast(
    void* data,
    int count,
    MPI_Datatype datatype,
    int root,
    MPI_Comm communicator)
```

`MPI_Bcast`的实现使用了一个类似的**树形广播算法**来获得比较好的网络利用率。
![tree boardcast](https://mpitutorial.com/tutorials/mpi-broadcast-and-collective-communication/broadcast_tree.png)

`MPI_Bcast`给每个进程发送的是同样的数据，然而`MPI_Scatter`给每个进程发送的是一个数组的一部分数据，如下图所示。
![MPI_Scatter](https://mpitutorial.com/tutorials/mpi-scatter-gather-and-allgather/broadcastvsscatter.png)

```cpp
MPI_Scatter(
    void* send_data,
    int send_count,
    MPI_Datatype send_datatype,
    void* recv_data,
    int recv_count,
    MPI_Datatype recv_datatype,
    int root,
    MPI_Comm communicator)
```

第一个参数，`send_data`是在根进程上的一个数据数组。第二个和第三个参数，`send_count`和`send_datatype`分别描述了发送给每个进程的数据数量和数据类型。如果`send_count`是1，`send_datatype`是`MPI_INT`的话，进程0会得到数据里的第一个整数，以此类推。如果`send_count`是2的话，进程0会得到前两个整数，进程1会得到第三个和第四个整数，以此类推。在实践中，一般来说`send_count`会等于数组的长度除以进程的数量。

函数定义里面接收数据的参数跟发送的参数几乎相同。`recv_data`参数是一个缓存，它里面存了`recv_count`个`recv_datatype`数据类型的元素。最后两个参数，`root`和`communicator`分别指定开始分发数组的了根进程以及对应的communicator。

`MPI_Gather`跟`MPI_Scatter`是相反的。`MPI_Gather`从好多进程里面收集数据到一个进程上面而不是从一个进程分发数据到多个进程。
![MPI_Gather](https://mpitutorial.com/tutorials/mpi-scatter-gather-and-allgather/gather.png)

跟`MPI_Scatter`类似，`MPI_Gather`从其他进程收集元素到根进程上面。元素是根据接收到的进程的秩排序的。`MPI_Gather`的函数原型跟`MPI_Scatter`长的一样。
```cpp
MPI_Gather(
    void* send_data,
    int send_count,
    MPI_Datatype send_datatype,
    void* recv_data,
    int recv_count,
    MPI_Datatype recv_datatype,
    int root,
    MPI_Comm communicator)
```

在`MPI_Gather`中，只有根进程需要一个有效的接收缓存。所有其他的调用进程可以传递`NULL`给`recv_data`。另外，别忘记`recv_count`参数是从每个进程接收到的数据数量，而不是所有进程的数据总量之和。

多对多通信的话，则采用`MPI_Allgather`，它会收集数据到所有进程上。

![MPI_Allgather](https://mpitutorial.com/tutorials/mpi-scatter-gather-and-allgather/allgather.png)

```cpp
MPI_Allgather(
    void* send_data,
    int send_count,
    MPI_Datatype send_datatype,
    void* recv_data,
    int recv_count,
    MPI_Datatype recv_datatype,
    MPI_Comm communicator)
```

* 阻塞到所有进程完成调用：`int MPI_Barrier(MPI_Comm comm)`
* 一对全部广播：`int MPI_Bcast(void *buf, int count, MPI_Datatype datatype, int source, MPI_Comm comm)`
* 全部对一约简：`int MPI_Reduce(void *sendbuf, void *recvbuf, int count,MPI_Datatype datatype, MPI_Op op, int target, MPI_Comm comm)`
* 全部对全部：`int MPI_Alltoall(void *sendbuf, int sendcount, MPI_Datatype senddatatype, void *recvbuf, int recvcount, MPI_Datatype recvdatatype, MPI_Comm comm)`
* 将数据分配到不同进程：`MPI_Scatter`
* 将不同进程的数据合并到同一进程中：`MPI_Gather`，若全部拷贝一份则用`MPI_AllGather`
* 划分群组：`int MPI_Comm_split(MPI_Comm comm, int color, int key, MPI_Comm *newcomm)`

## 其他操作
两个基本操作send和receive，有三种类型
* buffered blocking：拷贝到通信缓存后立即返回
* buffered non-blocking：初始化后DMA后就返回
* non-buffered blocing：收到receive操作后才返回

解决死锁：
* 顺序调整：P0 send完receive，P1 receive完后send
* **同时发送和接收**：`sendrecv`
* 将自己的空间作为发送缓存：`Bsend`+`recv`
* 非阻塞操作：`lsend`+`lrecv`+`waitall`

## 参考资料
* 官网，<http://www.mpich.org/>
* MPI Tutorial, <https://mpitutorial.com/tutorials/>