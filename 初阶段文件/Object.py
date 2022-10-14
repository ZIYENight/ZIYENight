# -*- coding: utf-8 -*- 
# @Time : 2022/4/26 13:34 
# @Author : 子夜
import time
import Rhino
import System
import scriptcontext as sc
import Rhino.RhinoDoc as rd
import Grasshopper, GhPython
from Rhino.DocObjects import *
import rhinoscriptsyntax as rs
from Grasshopper import DataTree    # 树形
import System.Drawing.Color as cor      # 颜色库
import ghpythonlib.parallel as ghpara   # 多进程
from ghpythonlib import treehelpers as ght  # 数列互转
from Grasshopper.Kernel.Data import GH_Path     # 树形分支
from ghpythonlib.componentbase import dotnetcompiledcomponent as component


# 获取数据详细信息
class Data_message(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_获取数据详情", "Data_message", """获取数据详细信息.""", "ZiYe", "Object")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("a946c7ad-a18f-471c-a9e7-038677fce6a4")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Data", "D", "数据")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Group", "G", "信息结果")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        result = self.RunScript(p0)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAJmSURBVEhLtVZPSzpRFJ2dBn6EzO+gGPYFJEVpabSJ/tEfRENwI1i5EGuyNEgXbZRaCWm4KdRCRVA0UHBhfoYIFNoUYae5w/sNTJZW+jtwdM513ju+d9+9M9zb25vl/f09SIzH48G1tbXg6uqq+P1b0rj19fVgIpEQ5yNywkcEAgKBAI6OjpBOp3F9ff1nXl1dYX9/H6FQiKYF1+v1eAHiD+NELBZDNBoFF4lEeLr4Hzg8PARntVr5crnMQuMFbRk3OzvL12o1FupHs9nExcUFzs/P+0jxdrvN7uxHNpsFZzKZ+Gq1ykJy0D9QKpVQq9WYmpqSUaPRYHJyEiqVCt/tQCaTGWxgsViwsrLC1NeYm5vD8vIyU3IMNTCbzfD5fBCOMl5eXvD6+iqRNGFrawuLi4vi9Wf8aAVUH6VSCQ6HA06nUyJpys/29jaWlpbYCDl+ZLC7u4unpyc0Gg3U63WJpLvdLjY3N0czoLOcSqVgMBgwMzMjkXSxWITb7R7NYGdnB51OB61WCw8PDxJJPz8/Y2NjYzSDg4MD5HI5zM/PY2FhQSLp+/t7uFyu0XPw+PgIuocK8h9J08qG5oAqedgKqCJtNlsfyWjoCgYZUB1QDgZB6P+D62CQgbB9sNvtTH0NWsmfDS4vL6FQKKDT6aDX62Wcnp6GVqvFxMQE7u7u2Ag5RAOj0Tiwm1IVh8Nh8Qn1mScnJ+JJ+g5SN61UKiw0Xtzc3IDz+/382dkZC40Xx8fH4IRq5L1eL25vb1l4PEgmk2Kj5IS2K75VeDwenJ6eilVbKBSQz+d/TRpH+0752dvbE2YFPgDn94A0immrtQAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Objects):
        if Objects:
            Group = Objects.TopologyDescription
            return Group


# 物件键值对提取
class Data_KV(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
           "ZY_提取键值对", "Data_KV",
           """对物件的键值对进行提取，当Key没有值输入时。提取所有的键值对.""", "ZiYe", "Object")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("af5ef186-5ae8-4eab-a2e8-42b171fa942a")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Guid()
        self.SetUpParam(p, "Object", "O", "物件集合列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Key", "K", "需要提取的Key-键,支持多键查询")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Keys", "KS", "提取的键；当Key没有值，它提取所有的key。反之只有Key")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Value", "VS", "所提取的键")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAALaSURBVEhLtZbBSxtBFMYXL1ZRqIbERulFiaDgSYIELVQToqX0YFsNJfageJGCOcSqTUwaY7IJ29pSNOIfIIIgCNJLESlK0YPY0ksPeggEqUcxYklU/LrvOaltkaVL4w9edt+8ee+bnZmdjXR6enr//PxcIUskEkpLS4vS1GRVbLYm9arPrFYr51OdXE1J/UlAZWjIi+5uF16GQpBjMcTicUQmJjA6OoKRkX83j8eD9vZ2vhIkoATGxnDnrh3D/jAi8UnEXr1DMBzH+w8fuZNeDg8P0dXVxYLS3NycQiN/5hmGwVAOk9HIZii/iQrzbXz++k2k6SOTyaCjowOS0+FQIhEZwy+CqDAZUVtbK8wCc2UVPm1uiRT98BPYbDZl8s1bPPeFUFx8A1WVZjbzLRPKDUZsbn0R3fUTCAQgNTc3K7IcRTL1HQ9dT9H5+Akeudy496AToehr/MhkRXf9jKlrywKkdB2wAE1RMBgUTflFU2B9fR2Li4vCA6anp7G0tCQ8YG1tDeoOFB6QSqUwNTXFWzSHpkBfXx8sFgvf9/f3Q5IkLC8vs0/Mz89z297eHvterxeFhYVIp9PsE5oCg4ODaG1tRTQaRVFREVZWVkTkgmw2i9LSUszMzLBfU1PDOb+jKeD3+1FSUsKjbGhoEK1/4na74XA4eHoKCgqwsbEhIhdoCvh8Pk6iEZaVlUGWZRG5ZHV1FSaTiaezrq4O6sEpIhdoCgwMDKC+vp7vZ2dn+Ul2dnbYz0EFq6urORZSD8m/0RSgIK2Behiy39jYCJfLdeUo6Qm3t7dFyyWaAsfHx9jf3/8lQIfX7u4uTk5O2M9BgrSTzs7ORMslmgL5gAXoS3StAurcKlctUD6ggUtOp1Oht/A6oLrSwsKCYrfbcXBwIJrzA9WjuvxNHh8fR1tbG5LJpAj/H1SH6tHUS0dHR/yvIhwO877v6enhN7O3t1e3UR7lUx2qBwA/AdFfSvBR19pyAAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def NoneKey(self, Object):  # 提取对象键值对
        Key, num1 = [], 0

        for i in Object:  # 获取key值
            Key.append(rs.GetUserText(i))

        Keys, Value = DataTree[str](), DataTree[str]()
        for ke in range(len(Key)):  # 获取Value
            for k in range(len(Key[ke])):
                Keys.Add(Key[ke][k], GH_Path(num1, k))

                Value.Add(rs.GetUserText(Object[ke], Key[ke][k]), GH_Path(num1, k))
            num1 += 1
        return Keys, Value

    def HaveKey(self, Object, Key):
        num1 = 0
        Keys, Value = DataTree[str](), DataTree[str]()
        for ke in Key:
            Keys.Add(ke, GH_Path(num1))
            for i in range(len(Object)):
                Value.Add(rs.GetUserText(Object[i], ke), GH_Path(num1, i))
            num1 += 1
        return Keys, Value

    def RunScript(self, Object, Key):
        if Object and Key:
            Keys, Value = self.HaveKey(Object, Key)
        else:
            Keys, Value = self.NoneKey(Object)
        return Keys, Value


# 键值对赋值
class DATAKEY(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
               "ZY_赋值键值对", "DATAKEY",
               """对物件的键值对进行f赋值，当多个物件赋值时，注意键值对顺序和数据结构；""", "ZiYe", "Object")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("4b68c580-a4e4-4ca8-9e49-082b8f014c0b")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Guid()
        self.SetUpParam(p, "Objects", "O", "物件集合列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Keys", "K", "Key-键,")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Values", "V", "Value-值")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        pass

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAQUSURBVEhLrZVdTJNnFMdbFOMWswxxi0MWl2WJyzYudrVkN9vFFiIZy5Il+8CbuQsNuMQFgbYU+gmlfQvFUtqC0NZ+sFSkiDh12uIHMj4ECS0MRFCgRXCgwFg7Wdz23/O8nZWuVUzk4p8+fc/p88v5n/Oeclytpt0Wm44x1DLrLnovx3RUp9Ub9FAxqnUXvZdTb6lWMAwDsVi87qL3RgFEYtG6KS6gWFSEomLhY0XjEqkobmy1aI5YsgpA/aKBc1e0GJqywnvTBu84+Vwt8mxg3IwWjwTXRuvhuxUnh2gk0ABPjxoiSQEYtQqcOlMYIBQK4Rt3YSZ0DJNLNkwtOaI0E3LC3S2H3cXH/MpZTCxaY3L8yw2YWLChxr4fRaJD0YBCoQC+sRaS2IDxewZM/2HGzQVj5Dz3lxUWVw5MP/AwF3Lj1mINAiETxu4aWAVCdbh934z+CTXkmq8hlvJiAd7RFtwOOjE6p8fFfgVuzNdi9k8bOZeia1gN55lcmJ083F1pQ+ewCp1DDPy/m1h1jzDovVGB4VkdFNo9jwfMP2jChWsyJCVvwfVZI35sF4HD4eBo00GcvMRjAUF0QsJ8hR2pyZgOWUh1dux6KwVFii/ZqtYEtPXJkPzSC7g6Wo5XUrbi86z3sQAXHK0HWcDyP5fh7pEiYUMCfh5SYihQjeee34TzXTLW1jUBF/vlePW1bfjw43ewPSWJ9MCCXx/YIwBqkT9Yh5TUJFRb9sF5uiCcR6r5ZeYpLLriU2Bj4gbWGlrJoF9HbHBEALTJ9+DAZ1+8h6y9H+C7vE+QnvkuqbIRvoA2DkAVDWj3loKbwEWJZg/xNhV7sz/CIprhOPkIMP+3HTrTPux8/WW8+fYOMPpvCMAZCzhiqooB0B68uHULAkEzyo3fgsPlkMky4vi58BRRgD9oQu9YBRI3bQSXyyVTxrA2PhXA0yvB5s2J6BurxNSyibUrJ3c3TncIIgDaTHrhG7u2I3XnNnacA0HL2oA7K41k/vVodgvIS1ZLLnGw03GmQxT1Hkz+dgSzKza09crhuSpjATP3rWyTSw/HAdBVMTjeCu+kEV0jCgxOH0b3dSV5oRTwTlVi5E4V6o/th61JiOmlU+gYkrOxgSkNiWvYc8+oEpcGZCiryloFqA8D6Ir1dFXiVDsfzR4eTrT9X3w0/vQ9jp/l4UJfGVzu/Jgc+rvWywJYT2RDJM17BGDXNVmvJUo+GI0QqgoqQYxoTFnOQ5maT77Hz6HPGU0hWdnF4XX9ECCRSNg9XiwqJNUICbDoCXpS/L/Ywz8ci7VGQf3PyMiATCZDeno6cnNz2TNNehZFAPkF+cj8NBN5eXlIS0tDzoFsyEvWCVBn1mp1Oh2kMimUKiWxScI2XF2uZpv0LDIY9fgXDacNWwRC6S4AAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Objects, Keys, Values):
        sc.doc = Rhino.RhinoDoc.ActiveDoc
        if Objects:
             rs.SetUserText(Objects, Keys, Values)
        ghdoc = GhPython.DocReplacement.GrasshopperDocument()
        sc.doc = ghdoc
        return



# 拷贝模型
class Bake(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
               "ZY_烘焙物体", "Bake",
               """烘焙物体，Bake为True时进行烘焙。其中图层等信息可选填。""", "ZiYe", "Object")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("09c16def-05d1-47b3-9db1-bf444ba5f240")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Geometrys", "GT", "Script variable Python")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "LayerName", "LN", "烘焙图层名字")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "Name", "NA", "模型名赋值")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "ObjKey", "OK", "键值对-Key值")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "ObjValue", "OV", "键值对-Value值")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Colour()
        self.SetUpParam(p, "Color", "CR", "颜色")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "Bake", "BK", "True进行烘焙，反之不运行")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "result", "RS", "成功时输出提示")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        p5 = self.marshal.GetInput(DA, 5)
        p6 = self.marshal.GetInput(DA, 6)
        result = self.RunScript(p0, p1, p2, p3, p4, p5, p6)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAM6SURBVEhLrVZLS1tBFJ5C20W71YU/oYsug4i2C5eSQLpwW3XRVam4UHzgYyEqXoMPNOJGfGDdCi5KUUsWFVxEwYKgiNBKTPow5mUeN6/79ZzJpElMYmPrBxPOOXfm++aeOXNuRDKZNBuGYePR2dlpq6mpsVVVVdmqq6vvPHgdr2eeLKegHzsILS0tMJvNGBgYwMjIyD8PXs88ra2tTAsW0Nrb29HW1oZEIiGD/wvmYT7mFYuLi1pTUxMoVerx/YD5mFc0NjZqPT09Klwe4XAYJycnODg4wP7+ftFwOp04Pz9XszNgXlFXV6cNDQ2pUDEuLi4wMzMj87uwsICVlRWsrq4WDY53dXUVpJnPQ9TX12uDg4MqVAiHw4Hu7m7s7u6qyO2Ym5tDNBpVHtDf319eYG9vT+5A13UVAQyDDpCOSi9TC/ymsVhMeUqAU3RTIBAIoK+vD5FIRPrhWBzewCe4LztpWOHxvkQo7JTP8lGxwPr6OnZ2dqQdiXlxGXiOwPUjpNMCBgRFBX75X9HbpOWcLCoSSKfTGB8fRzwel74v9FESM2n+0OMC15GvZOdQkQBXzfz8vLSTKQM/rt5Q7osFQpGHuAqekp1DRQJHR0ey7BjhaAhR/QlZheSG8QDxhIAv+IH8HCoSOD4+xvLysrT1RIpy/YKsQgE9/hj+kEAw/Jn8HKampgo6QkkBr9crd8KI01z/tYmsQgFO2bfvr+mQc2R+vx/T09PKy6CkAGNiYgI+nw9pqvtf/nd0FjnyFB14JCaoqr7IuVnwZeTqy0dZga2tLaytrUk7Qim99FvoQJ+SoKCSfUZ34T1SVAD5GB0dhcvlUl4GZQVSqRS4P52eZqpEp/5yFXThp+8tAmGHjOVjY2MDS0tLystBCtTW1hYJMDweD+jLJKsqi8I9Z7C5uYnh4WG5qZuQAiaTqWw3dbvdsh9xFz07O/tTIdzQuG2PjY0VVU4+ZDdtaGjQent7Vag0tre3MTk5KW84F4CmabDb7Tg8PFQzSoN5hc1m0ywWiwrdDk5D/kX6G5hXUM/R+IPf0dGhwvcD5mNeQf1e/quwWq1obm4GvZH8cMzOzt558DpezzzMBwC/AR/JdU9zQ6YsAAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def tree_value(self, tree, number):  # 树形数据提取
        try:
            return tree.Branch(number)  # 提取分支
        except Exception as id:
            if tree.BranchCount == 1:
                return tree.Branch(0)
            elif tree.BranchCount > 0:
                num = number + 1 % tree.BranchCount
                return tree.Branch(num)
            else:
                return None

    def Baket_bute(self, listc):
        butes = Rhino.DocObjects.ObjectAttributes()  # 属性样式内容定义
        butes.Name = listc[1][0] if listc[1] else None
        Key = listc[2] if listc[2] else None
        Value = listc[3] if listc[3] else None
        butes.ObjectColor = listc[4][0] if listc[4] else cor.Black
        for i in range(len(Key)):
            butes.SetUserString(Key[i], Value[i])
        Gs = sc.doc.Objects.Add(listc[0][0], butes)
        return Gs

    def RunScript(self, Geometrys, LayerName, Name, ObjKey, ObjValue, Color, Bake):
        if Bake:
            sc.doc = rd.ActiveDoc
            BaCs = []

            for i in range(Geometrys.BranchCount):
                Geometry = self.tree_value(Geometrys, i)
                name = self.tree_value(Name, i)
                Objkey = self.tree_value(ObjKey, i)
                Objvalue = self.tree_value(ObjValue, i)
                color = self.tree_value(Color, i)
                BaCs.append([Geometry, name, Objkey, Objvalue, color])
            GS = ghpara.run(self.Baket_bute, BaCs)

            for i in range(len(GS)):
                LayerNames = rs.LayerNames()
                Layername = self.tree_value(LayerName, i)[0]
                if Layername:
                    if Layername not in LayerNames:
                        newlayer = rs.AddLayer(Layername)
                else:
                    Layername = sc.doc.Layers.CurrentLayer.Name
                rs.ObjectLayer(GS[i], Layername)
            result = "烘焙成功!!!" + time.ctime().split(" ")[3]
            ghdoc = GhPython.DocReplacement.GrasshopperDocument()
            sc.doc = ghdoc
            return result


# 插件信息
class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "ZY_Data"

    def get_AssemblyDescription(self):
        return """欢迎使用此插件"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return "子夜"

    def get_Id(self):
        return System.Guid("96aa2301-c437-4e3f-b2f1-253a0679d742")