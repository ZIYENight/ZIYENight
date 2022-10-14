# -*- coding: utf-8 -*- 
# @Time : 2022/4/21 11:57 
# @Author : 子夜
from ghpythonlib.componentbase import dotnetcompiledcomponent as component
from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree as ghdt
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs



# 列表取值
class list_values(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
           "ZY_list下标取值", "list_values", """列表根据下标取值，取值下标空格间隔""","ZiYe", "List")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("969903d7-b159-4520-be02-36ef0cad97bf")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "List", "L", "列表输入")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Index", "I", "取值下标")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "List", "L", "获取的值列表")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMVSURBVEhLtZbZTxNRFMbnL4HwZOJ/oC8GeCJGMzYFpEQxslWWBkyRRXYCDktAQJaqlFq2NOEBpcQItqQsRRRQIGAolZZaIjxYIlQ0Uvo5985YMAUUUn7Jl07PubnfvffMnBlmd3c3AgC3vr7OsSzLBQUFcSEhIadScHAwVUpKCkfmJGK8Xm+jx+OBUqmETqfDwsICLBYLlpaWTqXZ2VmoVCoUFxfz8wPM9vY2V1RUhJmZGRoIFGSxLS0tYGpqaji1Wi2GA0tlZSUYqVTKjY6OiqHA0tHRAUYikXBms1kMBZbu7m5hB+Pj42LoeFZWVmAwGGA0Gv00NjYGt9stjhTo6uo6mUFcXBzkcjlycnL+Um5uLsLCwtDf3y+OFDixQXp6OsgtfRgajYZOeJB/Gnj2vPi1uyf+AxQKBWQyGZKTk31KSkpCQkICQkND6fEdhBqwrIR7MyEU2ercRJnajKInY2jXz6OyYxKDkzaaI+zsfIfdZoXt0zIVuV5zOuHktbGxgb29/cUQqIHsehSnf2mAYdqJet0UBt/a0WdapgbGqVV4veJonty8PFxmoxApu00VcUUKjiMd4XB8BoZhE6p65uhqHRtbUDYOo7bnHbpeLYpDBWJupeJqxSIS2r4hUb2NiMJpJKcpxaw/viN6PzWJn3ztytrNUPV9wPpXN92BZmBeHCogjY7F+fA7uCC9j4uR+Th3KR7xiXIx6w81IA/anyK3vZhDads4dK8/oo7fQQl//XxkmeYIVusyRoaHfDIZh7D6eU3M+uNnQLA4XJiYXwM5enIHbW79EBI8vb29eFhbjdbmBrQ21dPfhrpqcOWl+6ooRVlJAW10nZ2d/gbHcTOGxaSCwZcHvMqPUAUDWyGDOEkoVE+1pAbsfxvERrPoucHAdJdXxhHKZDCUxiD2Wjgetz07mYG6XYPUjHvIyMo/VmmZOXjU1MzXgD8iYnCm3ZQYkE54FtAiFxQUcFqtVgwFlqqqKjDkayI7O5u+sAPJwMCAYMB/tjS6XC7aKfV6Pex2OxwOx6lltVrpqzIrK4u3AX4DaDWVAOFbm6IAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Lists, Index):
        if Lists:
            indexlist = Index.split(" ")
            List = []
            for i in indexlist:
                List.append(Lists[int(i)])
            return List


# 树形取值
class Tree_Values(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
                                                           "ZY_树形规划取值", "Tree_Values", """Explode-True 对树形数据拆分 统一路径.
Explode-False 取出branch路径的值""", "ZiYe", "List")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("0eff0c49-1b47-4d30-a4bf-ddfae9774fb2")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Tree", "T", "数据-data")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "Explode", "E", "True-将树形数据拆分整合，统一路径；False-根据Branch取树形值")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "Branch", "B", "取值路径信息")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Objects", "O", "输出结果")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, False)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAPuSURBVEhLvZbtT5tlFMb5BzQxJn6ZDlraUkZpmW+JsEEpfX8vMGDMycbalXcN9BXap7VrGJlaB5i5GEQ2J4Np5mLULYuy+fJ/XV7nkbHV1g8asg9X7uZ57udc9/mdc+604YuViufG8idXPsuVDl0St6H4bnS1MjSGcnjk0CVxG4pnxpcvBYew6A4fuiTuczTwhJF1hZC0+ZGw+pGyBep+9Kyy+2vBE0HB248ipXgjB++rDDLOIHIDI1hPTGBtPo6Pp6NIO0MHm/9NC9SY049zlKxxdwg5HlbeVRnI6TM8yU4lgT/vlvH7dyVcnYshZQ/WBM0wSN7Xjw99Axi3uXFUr4fGYECTTgejuQMTrqCaSZWBIFro8eKjiXHs7RTxiNqpJJG0P81CkCgMPMegbzVqmWEAsT4PmpqboWNwVS0tiJNGjUHGQeZDo7hzPYcfNhXc+1JB8fQo0vantSj4B5Fk0BM6IyyvNhJrAHGHH0aTGW2U4VgbHCesKPoH1P1VBoIoxSJtlT/Ao9tF7G0XsM5aCKIlZpdm2pPdDjha23HxZJ+KqRw4hQvMRtdihNFohIGnN3e8gUnuzfObKgNBlLD68OlsFI93i3hMRGKW6ONmGke7ehncjBmrCxPddrz20stY6PPiot1LRFoVTzNXjUGPGDOrQZQlt0V20fa1PHY+z2GXqFaTUzwpiyodRpPLkdNqJoIo3PGmGiTu8MHEwlosx9FmtiB00qa2bH1E7giuL83gxy0FD2/k8Nu3JWwos0g5QmpgQSOIJAv5LRim+PydLiu6OnvUNUhkWT6vMRBEqV4/Vs6fxc83C6rB3jcK7m/loUSGMdPthMfUgdleNwZefxuvvPDiAaKjmiZotRpouTayXc+x8ApbvspAMGQDg9hey+L7jTx+2sypRpWZKBKcbkF0pf8Mznda4TpmxpTViRK7KipFZoGNxlboDS04TlwyfDJsNQaZ4CBur2dxb4PBv8rhwdc0mI0hzUK/z0BOBpYsluRqYCvKKWN2n9qmpnYLWk3t6OnsRrZeDQRRUkX0Hu7fVPBgK4dfb+Xx8JaCwqkRzNu8ZO9UB00MJIAU+YLNBQ07SM9pNuh1aNpHJPdTtQE/kGJuFufwy25JneQ/7l7CnaspZBhI3gsmWZ9IukWuiiNaLRrZokdYAwszSfKwNYikixaJaD09jTW257UMlZ2GMjhcNc3PSoLMEa2f0xuiZJ3khSeZybVSk0GW0ykFFS0Ql1zbUhvB98/gf+8Pq1Ne5KX3RPn94PK+xuCw9XwMSmejy+XQsHp5SXdIyvU2/x+pBvORkdWV/lFcpuQqXiTDZf6u9y/hv6oyNIa/AHG1pSM2zID3AAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def treegroup(self, Group):
        GP = Group.Paths
        treetype = type(Group.Branch(GP[0])[0])
        Objects = ghdt[treetype]()
        gplist = []

        for i in range(len(GP)):
            for j in range(Group.BranchCount - i):
                gplist.append(GP[i + j].IsAncestor(GP[i], 0)[0])

        for gpbr in range(Group.BranchCount):
            grouplist = Group.Branch(gpbr)
            if Group.BranchCount > 1:
                for libr in range(len(grouplist)):
                    if gplist[gpbr] == True:
                        Objects.Add(Group.Branch(gpbr)[libr], GP[gpbr])
                    else:
                        Objects.Add(Group.Branch(gpbr)[libr], GH_Path(gpbr, libr))

            else:
                for libr in range(len(grouplist)):
                    Objects.Add(Group.Branch(gpbr)[libr], GH_Path(0, libr))
        return Objects

    def RunScript(self, Tree, Explode, Branch):
        if Tree.BranchCount > 0:
            if Explode:
                Objects = self.treegroup(Tree)
            else:
                GP = Tree.Paths
                treetype = type(Tree.Branch(GP[0])[0])
                Objects = ghdt[treetype]()

                if Branch:
                    for br in range(len(Branch)):
                        tu = [int(i) for i in Branch[br].split(" ")]
                        GH = tuple(tu)
                        obj = Tree.Branch(GH)
                        Objects.AddRange(obj, GH_Path(br))

            return Objects


# 列表切割
class List_Cut(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
                                                           "ZY_列表切割", "List_Cut", """在列表指定下标处切割列表，树形结构输出；
（原电池最后一个下标不做参考，已改）""", "ZiYe", "List")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("dd4e55e7-7e2c-4fb0-95ef-adaf2461397d")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "List", "L", "需要切割的列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "Index", "I", "切割下标")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "DataTree", "DT", "切割完成的列表为树形数据")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMuSURBVEhLtVZbKHRRFD6PPHngQR7UpBQvasoDhZQwUkrNi5DLuEW5lmJSGNklTwgR8ULTuDy4RLk+uF9CuUxTI+WBKEJD5HPW6tA/nPPza/6vVqe99tnft9dea69zpOfnZwMAcXZ2JpKTk0VgYKDQ6XQiKCjon43W0XriIT7ilV5fX9seHh5QWVmJkZERHB4ewm63u5nD4fji0zJab7PZUFFRAeKVLi8vRU1NDU94EsRHvFJVVZUYGhpS3OpIS0vDwcGBMvo5iFeKjY0V29vbiusrenp6IEkSuru7Fc/PsbW1BSkmJkbs7u4qLnfIiYKPjw/8/PxgMBjw8vKizPwMtHGOYGdnR3G5IykpCd7e3ggODkZoaCguLi6UGXVMTExACIHl5WUecwRaAr29vXw0ISEhCAgIgF6vx93dnTL7FY+Pj5C5kJKSgtTUVPZpRnB6egovLy/4+vrC398fco1jeHiY5+SyVj2q+/t7ZGZmYnNzE1lZWezTFEhISODkbmxsYG5uDufn5+w/OjpCXFwcIiMjMTo6yr53UM2np6fz+38VaGlp4Z2oYXJyEvn5+XzOjY2N7Lu9vYXL5WL7VuD4+BhhYWG4ubnh8WdMTU2hrq6O67ujo4Of4eHhHDFFl5eXpy6wt7fHSYqOjsbY2BhPqmF6ehq1tbUYHBxEV1cXR9Hf34/c3FwsLCygsLBQXYDUT05O+Gp/BpEkJiaivb0d8/PzHwKdnZ1obm7m0iwvL8fS0hIKCgq+z8GfoGqROyOfeUZGBmZnZ2E2m90ExsfHUVpa+jsBuZVzwtfW1lBSUoKZmRnPC9DO6WiKi4t/J0C9SEuAkJ2dzREQCbWAhoYGWK1W9PX1obW1lUXljswXjDaxuroKk8nEaz+anZaA0+lEREQEmpqauNnV19fDaDSirKyMK4aio6RTniia+Ph4WCwWREVF4fr6Gvv7+5DkgWY3XVxc5BxQGRYVFXGd0zG8P8lotyRGPnonJyeHo6Y7RcYRUCj/A9Rq+Is2MDCguDwL4pWurq5EdXU1J8mTID7ilZ6entqoUdFfBV37lZUVrK+v/9poPVUY/VW4XC68ATTjNbvne9s8AAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def ListToTree(self, List, index):
        DataTree = ghdt[object]()
        for i in range(List.BranchCount):
            list = List.Branch(i)
            if len(index) == 1:
                data = list[0:index[0]]
                data2 = list[index[0]:]
                DataTree.AddRange(data, GH_Path(i, 0))
                DataTree.AddRange(data2, GH_Path(i, 1))
            else:
                for j in range(len(index)):
                    if j == 0:
                        data = list[0:index[j]]
                        DataTree.AddRange(data, GH_Path(i, j))
                    elif j == len(index) - 1:
                        data = list[index[j - 1]:index[j]]
                        data2 = list[index[j]:]
                        DataTree.AddRange(data, GH_Path(i, j))
                        DataTree.AddRange(data2, GH_Path(i, j + 1))
                    else:
                        data = list[index[j - 1]:index[j]]
                        DataTree.AddRange(data, GH_Path(i, j))
        return DataTree

    def RunScript(self, List, Index):
        if List:
            DataTree = self.ListToTree(List, Index)
            return DataTree


# 数据清洗
class Data_rinse(component):

    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
               "ZY_数据清洗", "Data_rinse", """去除空值和空格值""", "ZiYe", "List")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("13b14752-b265-4040-bfea-81d0c089b31b")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Data", "D", "需要清洗的数据")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Data", "D", "清洗后的数据.")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        result = self.RunScript(p0)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMhSURBVEhLrZZtSFNRGMevqb2QlmUfEstYkoTZmCxCRMMGYmEFIiWxKI2QqEDwLQikDxLB/ZIMLMrCQCi0zM1Ic+BSP2iEKblhkHtlu1PnbDqn05n7d3d3UMGr3lk/eC73/p/D8+c853DOpRYXF3P9fj/d19dHS6VSOjExkU5JSdkwxGIxLU1N5c2JRCJaJpPRJpOJDtSl2EetzWZDaWkpOjs7YbVawTDMhuF0OmGy2HhzZrMZSqWSqzc/Pw9Kp9PRlZWVcDgcEMqnDg1u3SkjX/xotVpUVVWBys/Pp9VqNZE3x2hhsCcmFhHbd2HKPUtUfurr60EF+mkwGIi0MZ65BZxMPQ2KorhobG4lGX66u7tBSSQS2mg0Eml9Zue8yMnNWy4eiLzLcpLlp6enJ2ggZAbNH9XYdyCOLRy2YhK1H6OuGTJiLcszEGKwtOTnWjTwYxivGhpx7XYp7iXE4nuLkoxYC2cQyhqsxvXkIZCxF5rMJKRlnUdJ+QO8fafCz18m+P4Ex3R3dYVu4GZ3jr5EDscJCqO5yRhWtSAyKma5bWHhOxB3SARlmwaDgwOhGbgcTuhv5mIimYLxghjj2iFOL5AXrqwLGxJpGqbdHvT19go3cJotMBRkcsUNl9PhXLXzPrR+Xi4en5CIUcckp3cJbdG4TgfjRUmw+I0cuEbHSSbIzKwXu6NjsC08Et8GtEQVuMj2r70wZR/jeq6/ewXTU/zb8ur1YiieviRfQTY1sKnbYDkTj/GUMOjvF8Pj9ZHMWtyeefK2wroGS2xY3r+BNS0WY+IIGB5VwhsQQ4TXwLfgg/lFDZhT0bCn7oRR8RgLJBcqvAbuiUnos0RgxJEwvX6GRaJvhXVbNPZFDUtTA9eqf4EzCFxzQk7TrcCdpoEZjIyMEOn/otFoQBUVFdFNTU1EAvxsuNkjYcrGYIqxCw6X1QbPb1ewCEGhUIBiL2q6oqIC/f39RAbMchnsZw/DnpMkPDIOwlpWSCoAKpUK1dXVCPy21Hq9XpSXl+N5XR3a2zswlJcOW/ZRmM8dFxyM7Aj6Cy+xPwRq1NTUcBc+APwFoY95IeNYRy4AAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Data):
        Datas = ghdt[object]()
        serial = 0
        for data in Data.Branches:
            one = [da for da in data if da and da != " "]
            if one:
                Datas.AddRange(one, GH_Path(serial))
                serial += 1
        return Datas




import GhPython
import System

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "ZY_List"

    def get_AssemblyDescription(self):
        return """子夜"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return "子夜"

    def get_Id(self):
        return System.Guid("af055435-d5fd-4f67-a65d-2fcbd65b0845")