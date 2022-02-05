# mouseVR
**现有的经验：**

- 需要把小鼠的重心放在球的上方
- 胖鼠似乎更难动

**目前的问题：**

- 气浮球只打一个孔的时候不稳定，球会自己转起来
- 小鼠的运动还是不太流畅

**两种优化思路：**

1. 参考商业版气浮方案，多打几个孔：
2. 不用气浮方案，用滚轮方案（参考下面的开源项目）

**商业版方案**

- $\Phi 4$ 的孔
- 孔与中心的夹角为30度

**开源的滚球方案：**

[Large Spherical Treadmill for Rodents](https://www.janelia.org/open-science/large-spherical-treadmill-rodents)

#行为球连接方案树莓派使用说明

- 硬件：Car用的是Pi3（带壳的那个）, VR用是Pi4
- 网络：树莓派目前默认连lk的手机热点，需要重新配置一下
- 需要配置ssh和ftp, ssh推荐termius, ftp mac下推荐ForkLift, win下不清楚哪个好用

**基本原理：**读小鼠的位移为指令量，计算与当前位置的差值，根据此差值通过PID控制计算速度。

**其中：**

- 读鼠标：两个鼠标通过读linux文件的方式读取
- 差值计算：位移量的差值需要自己维护（deltaComputer类）
- 目前旋转、位移分开控制

# 代码说明

## Raspi

**读写和小鼠直接交互的硬件，通过socket连接与Unity通信。实验时需要先运行main.py**

- hardware.py: 读取鼠标输入，读写GPIO
- socket.py: 实现socket通信功能
- main.py: 主函数
    - 持续读取两个鼠标的输入，发送给unity
    - 接收到给水命令时给水

## Unity

![https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2581918a-93bc-4b34-bea5-0108d655dd94/Untitled.png](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2581918a-93bc-4b34-bea5-0108d655dd94/Untitled.png)

代码在Asserts里面。主要的三个模块：

### Agent.cs: 实现RL和人鼠控制的接口

- Eposide Control: 控制一个实验节什么时候结束，重新开始一节时刷新环境
- Act: 两种模式二选一
    - OnActionReceived: 根据来自RL接口的控制指令actionBuffers运动（机器控制）
    - Heuristic: 根据人为输入的指令创建actionBuffers作为控制指令（人或鼠控制）
- Reward: 提供RL需要的Reward.

该模块通过agentsUtils实现具体的运动控制、相机移动 | 发放奖励 | 实验节控制等功能

```csharp
public class MiceAgent : Agent
{

    // -------------------------- Init --------------------------- //
    AgentUtils agentUtils;
    public override void Initialize();

    // --------------------------- Eposide ------------------------ //
    public void CheckEposideEnd();
    public override void OnEpisodeBegin();

    // -------------------------- Act ----------------------------- //
    public override void OnActionReceived(ActionBuffers actionBuffers);
    public override void Heuristic(in ActionBuffers actionsOut);

    // ----------------------- Food ------------------------ //
    void OnTriggerEnter(Collider other);
		// ------------------------ Reward -------------------------- //
    private float reward = 0;
    public void Reward();
}
```

### AgentUtils: 具体执行对应功能

- 通过绑定MainCamera，CharacterController控制自身以及相机的运动
- 绑定foodPrefab, 监测一个trial是否完成，完成重新生成foods并重置自身位置
- 绑定IOManager, 实现与小鼠的交互

```csharp
public class AgentUtils : MonoBehaviour
{
    // Binding objects
    IOManager IOManager;
    public GameObject foodPrefab;
    public Camera MainCamera;
    public Transform CameraPosition;
    CharacterController m_CharacterController;

    // ------------------- Init functions ----------------------------- //
    void Start();
    void BindAll();

    // --------------------  Move Related  -------------------------------- //
    public void HeuristicMove(out float move, out float rot);
    public void PerformMove(float forward, float rotate);

    // --------------------  Eposide and Food related --------------------- //
    public void OnFoodCollected();
    public bool AllFoodCollected();
    public void ReGenerateFoods();
    public void ResetMe();
    public void FoodCollected();

}
```

### IOManager

- Client实现与树莓派的通信，命令的格式为"{some command}/n"，因此需要对目前接收到的命令进行拆分【recvCmd()：读数据流，返回已经接受完成的数条命令】
- IOManager：接受底层输入，整合来自人（键盘手柄）和鼠的运动
