# -*- coding: utf-8 -*- 
# @Time : 2022/4/26 14:44 
# @Author : 子夜


class MyComponent(component):
    def __new__(cls):
        instance = GH_Component.__new__(cls,
            "插件名称，如：颜色设置",
            "插件 Nickname",
            "插件功能描述，如：设置软件的背景颜色",
            "插件一级分类，如：数能化插件集",
            "插件的二级分类，如：环境设置"
            )
        return instance

    def __init__(self):
        """
        定义初始化行为，添加实例属性
        """
        super(MyComponent, self).__init__()
        # 输入你的代码...
        pass

    def AppendAdditionalMenuItems(self, toolStripDropDown):
        # 添加电池右键菜单
        component.AppendAdditionalMenuItems(self, toolStripDropDown)
        # 添加分割线
        toolStripDropDown.Items.Add(ToolStripSeparator())
        # 输入你的代码...
        pass

    def get_ComponentGuid(self):
        return System.Guid("你的31位GUID字符")

    def RegisterInputParams(self, pManager):
        """
        注册本电池的输入参数，以 Point3d 为例...
        """
        p = Grasshopper.Kernel.Parameters.Param_Point()
        p.Name = "Point"  # 设置参数名称
        p.NickName = "P"  # 设置参数 Nikcname
        p.Description = "由 @Vctcn93 钦定的点"  # 参数描述
        p.Access = GH_ParamAccess.item  # 参数数据类型
        p.Optional = True

        default_velue = rg.Point3d(0, 0, 0)
        p.SetPersistentData(Types.GH_Point(default_value))  # 为参数设置缺省值

        self.Params.Input.Add(p)  # 添加入输入端

        # 输入你的代码
        pass

    def RegisterOutputParams(self, pManager):
        # 写法同上，Input 变 Output，请输入你的代码
        pass

    def get_Internal_Icon_24x24(self):
        o = "字符串化的图片..."
        return System.Drawing.Bitmap(
            System.IO.MemoryStream(
                System.Convert.FromBase64String(o)
            )
        )

    def Read(self, reader):
        # 基本的选项状态读取，以 int 和 boolean 为例
        ok, index = reader.TryGetInt32('my index', index)
        ok, status = reader.TryGetBoolean('my ststua', status)
        # 请输入你的代码
        pass

        return super(MyComponent, self).Read(reader)

    def Write(self, writer):
        # 基本的选项状态记录，以 int 和 boolean 为例
        writer.SetInt32('index', index)
        writer.SetBoolean('status', status)
        return super(MyComponent, self).Write(writer)

    def SolveInstance(self, DA):
        # 获取参数
        param = self.marshal.GetInput(DA, index)

        # 核心方法，在这里实现你的功能：
        pass

        # 输出参数
        self.marshal.SetOutput(result, DA, 0, True)


