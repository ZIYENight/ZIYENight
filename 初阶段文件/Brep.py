# -*- coding: utf-8 -*-
# @Time : 2022/4/20 14:50 
# @Author : 子夜
from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import ghpythonlib.parallel as ghpara       # 多线程
import Grasshopper.DataTree as ghdt         # 树形类
import ghpythonlib.treehelpers as ght       # 列数互转
import Grasshopper.Kernel.Data.GH_Path as ghpath        # 树形下标
import Rhino.Geometry as rg
from functools import reduce    # reduce

# Brep切割
class Brep_Diff(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_Brep实差切割", "Brep_Bool", """Brep的实差切割体..""", "ZiYe",
                                                           "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("8258170c-1c5b-4391-9389-b2b67aae0f42")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "A_Brep", "A", "第一组Brep物品")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "B_Brep", "B", "第二组Brep物品")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "PRE", "P", "精度[0.00-1.00]，当切割失败时，调动。其他情况勿动")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Brep", "B", "差集切割物体")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAMRSURBVEhLrZXZTxNRFIcHJUERJPFJE41LjL76aGKCb5q6Rv8lo8HEBQXXYBDrQjTGuKQt7cydGdrOTKellm6zVGOAxGhbUOOLbYGfZwoo0CIIPHyZSZP5fb33nnMPV6lUXJUpdJQqU+uOk8tl7JEuesH495/rzuQ0wOkJoyOfz8M0TVimAdsy14yTYxKFQh5cLGmRoADLsmBaNtJZC8l0Fqm0sSqSaROGlavmFQqFGYHz4qwgY49BkDX4eYaAIK0KHy9BH7arf3ZWYFQFlp0DL0cgiQL0iAZdj8w8FxHVNQzKEkSR1UGsfu8XZGRoJ4rF+QIyykEFr996cPnKTVy93oVrnd2L6MKVztt45xkgiVwNrIVBEB2BWStQtCgeuvtxuP0Yduzah5279y9kzwFsbtuO+z0PoalqnfBlBGE1iqf9L+A6dQ4cx9VhI7gNm/Cgt29tguMnztYJ/8vdnl4oJOAZq0GURDDpPwUNGxrRfuQozrhO4rTrDN68fI24GoEmBxcQDYXBAiIGeBFZY05AjbacoHlLK3KRIUx/+oiylcW3eAzFaATjMf0PE0NRfKUqe3SDisDHwzDnqmglguYtyARDKCd1lONh/KpDJaGiGBLQfeEiPH62tOCZc8inz4NraCToUInmljakB4OopKIov1dQqsPksIYJRcSdSx1LC5wy7XvyHHsPHkJjU2uVjU0t2LptO9K0gjULnEbzeAeoDN3ocz/9y+N+jCaGUUpomKagqTogreOHJv1bIMphSBKDqioLUBQVY4kkvgwyjIcYiuFaJhQJo4IPtxafgXNdzxcwJixoHIlwGsf/ygOf2w3f4ydLMkC47/XC6xfrCwIsVCNwYISfF6iRxGURJbpVmUTX/mwfzBeEoynwdFVLJJGo5ecj09atBEHgwYI6sqaNIuWSIFMVGAZNoQ8jiA2b8PJBeAIyvIHBFeNx8MuQ1TiyuRHaIlrBnGBuojnt7QyKjGEhlTH/H5oBJk0zg3L+TLQZQb76gz1Lzl49tgNlzAhoJsdTdldpEvj8dXzdKU0CvwFtCDTndcE1nQAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def tree_value(self, tree, number):    # 取树形数据的指定项
        try:
            return tree.Branch(number)
        except Exception as id:
            if tree.BranchCount == 1:
                return tree.Branch(0)
            elif tree.BranchCount > 0:
                num = number + 1 % tree.BranchCount
                return tree.Branch(num)
            else:
                return None

    def boolD(self, list):      # Brep切割
        A = list[0]
        B = list[1]
        PRE = list[2]
        diff = rg.Brep.CreateBooleanDifference(A, B, PRE)
        return diff

    def RunScript(self, A_Brep, B_Brep, PRE):
        Brep = ghdt[Rhino.Geometry.Brep]()      # 定义初始化
        clist = []
        PRE = 0.02 if not PRE else PRE
        if A_Brep.BranchCount > 0:
            for i in range(A_Brep.BranchCount):
                lt = [A_Brep.Branch(i), self.tree_value(B_Brep, i), PRE]
                clist.append(lt)

            res = ghpara.run(self.boolD, clist, True)     # 多线程运行

            branch = 0
            for i in range(len(res)):
                if A_Brep.BranchCount == 1:
                    Brep.AddRange([res[i]], ghpath(branch))
                else:
                    Brep.AddRange([res[i]], ghpath(branch))
                    if len(res) / A_Brep.BranchCount * (branch + 1) == i + 1:
                        branch += 1
            return Brep


# Brep结合
class Brep_Union(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_Brep结合", "Brep_Union", """将多个Brep结合成一个.并消除参考线""", "ZiYe",
                                                           "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("57cfa2b7-7b3d-43ee-b190-3af9cfa5c6f9")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Breps", "B", "Brep物件，list类型数据")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.tree
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "PRE", "P", "合并精度[0.00-1.00].成功情况下不改动")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Brep", "B", "结构之后的Brep")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOmSURBVEhLrZXtT9tWFIf37+3PWL/vyyZVKxPTtHaFlU5qNdGmQDcgiUkCawuUlwFVEbB0G2szIDh23klIFuxAYjt2YjvOb8eXjBSaTGJg6VEc5fg891yf3PORIAgfl8vle/F4/Npx87qCh61WC7IsXztuXldw1/1Cn9jf568NURSYpC2QwItJZPJHyOZLV+OwhHSuBF5IdARHR0dIZfNwL7esVsth9/91uTGnseehX9B0WhATGUiS1BEkMznYdhOWZVGgg6h4gNX1MDbD22dsvfkTS2tb2OFTcByHxV7Eti00TAtCIn1BkD6gABumabKV7PFJjPtnMO4NYMIXZHChZ/ii/w5ezC+xKtzYi1iWiXrDhBBPQ+4lcFcnJrMIUMLJSS/8fj9jejqEz2/2YX5h+XICqS0wqbRGo4Fms0klZpjA5/OB4zjGzMw0bt7qx9zCL0zgxl7ENBsw6g0SpC4n8FEFgeA0Pv3sFp7NrzCBaTtt6MU2HXq23luQIEGDSqvX6/SibMTiHYHPzyEUDODV8gzGHj/A+upLVKUs5AK14mEC5UIc+dwBDMOtog7dqHcRpLKUnOyGwbohRnt4KvBiwsthN/wS6n4QeiwEZY+D/HaCUY5MIrflwax/GEbDZgus6QY9f0mBsL0MK/oUdvQx7D1PB34EhfXvMDUyiLrl9BBIpwKDStN1nXUDL54XxP6g1oz9SHgA/kkHcRTy1hCCT4eogiZboFbTERO7CoxzgtDPLzA15YePC1AFS2j1EEhnAru3IE4CN3mtVmOdxFPA6DiHH4af4MHwKPbeLKAl/NRbMHYPet1iOVSt1kWQzLDkmqbBolbb/H0XX3/7Pe4M3Ef/7fuIbM4BiXFKSAKBEv9LYgzH4SEESFAzTJZDUTUSJD8UqJRcVVWSqJDkYxRLMkrSMQqlE5QSv+Fk2wP13TDUt486/OVBem0Q3MgANL3BFlhVVHY6u6d0WyDR0ZAhswpFUVCtVqHRfa2mMXTq73dbi3jl/Qqvp74hbp+xTqxOfInnnAeKZrAFVqpKFwGdftV28g9RkMsX2J8pn893IYfi3yUWqxAnlSrNg/cEblnu+a2zDqihUqmcJa+0UWlfNXp5vXC3141zBcdM4A6ctmBxcRFRPo7nc0tYWF6j2XDI2vT/EhVS2OdFlMs00TY2Nu729fUhHP4VN258gsGBARSLRTajr4IoiqcjMxKJPNzZ2aV9PMTs7BxWVlbIXKZpJF8Zp9XCP0E68839C3s/AAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def brepbp(self, Breps):
        Result = rg.Brep.CreateBooleanUnion(Breps[0], Breps[1])
        Result[0].MergeCoplanarFaces(Breps[1])
        return Result[0]

    def RunScript(self, Breps, PRE):
        PRE = PRE if PRE else 0.02
        if Breps.BranchCount > 0:       # 判断执行
            breplist = []
            for i in range(Breps.BranchCount):
                breplist.append([Breps.Branch(i), PRE])  # 参数添加
            res = ghpara.run(self.brepbp, breplist)
            Brep = ghdt[rg.Brep]()
            for i in range(len(res)):
                Brep.AddRange([res[i]], ghpath(i))
            return Brep


# Surface面积排序
class Brep_Arae(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_根据面积排序", "Brep_Arae", """根据face的面积进行排序,从小到大""", "ZiYe",
                                                           "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("f078e5e4-1f07-452f-a4d8-64babb1a4b9b")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Faces", "F", "需要排序的面")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Faces", "F", "排序后的面")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Area_Arc", "A", "排序后的面积")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        result = self.RunScript(p0)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANpSURBVEhLrZXdS5NRHMeHd6UZ1h8giAhS6TLfoJnhEsMrpQs1vJREvfRKTcWbKdWglXgjoqJ0K0GEVhAzl7UcMsu9uT2bL3PsBXTLTff2fDvnbE86N71wnvHl2Y/nPN/P77z8zhHNL2oe6y07I99Xfl+6qK9IvfpHwQNwu92XLp4Yi36trstoYDQaoNfpoEtTggf1o77/ATqDCZxtG9bNHXBpSPheT/zcblcM4HK5YDJziESj4ImiaYpOjYXbhNPpTAQEQyGEiUJpKhyOwMzZTgE2OBwFgwgRBc+QkGGqdycVCoUJwArXacDh4RHZT7HGk3EeHR3HtNG1cjgcJMNwSmNBqQFmK/twamoKw8PD4DiOxSqVCjKZDAsLC+jt7UVfXx/8fj+bCppAKgWDoWTAhsXGsiwoKIBIJMLY2BiLW1paWNzW1oaZmRn09PRgb2/vAgAyArr6FRXlzLCjo4MBSktLWdzZ2YnJyUk0Nzdj125n76LRSJKEXbhhIQBXCkBZWRmys7NRU1OD/f195ObmIjMzkwEMBgOWl5fh/evH1s4u7A4ndk6Ixtt2B5yePTYjCQC6BtEoj+LiYlRXV6OoqAhzc3PIz8+HWCxGa2sry5q2j58XcefeA9wtr0JJRXWCbokr8OTpM1ZsHqGSBUAkEkVhYSHa29uZaWNjI6RSKerq6thaCO3L1yVczbrBpi6VSisfwra9mxpAMx4aGkJtbS0yMjLQ3d2NhoYGNDU1xe0pQIWs7LMBlZJHiQB3HEArMC8vD3K5HF1dXazz9PR0CsASrl2/mWQsKAaww+NJANCjIoycnBy270dHR1lntVoNiUSC+vr6uD1PAN/OB9yXwrp1CmA0WUgBBTAwMID5+XlotVo2Co/HA4VCgfHxcValFPD+wydidCXJWNDtkqpkgMFoJgW0z3KkRoFAgP33+XzsSY8Oum0PDwPQaHWQvXiNkVdvMCJ/m6DhlwpMv5sjhbZ1fFxTgD4OoCbniVZxgBwV5zWe/IwmM6mDOMDr88JApujg4IBk7oeXGHm93ouLjNq4YYkBNFq9bG1tDet6E9QaLX6oV7BJtpjFun1hmYmoH7syVT9XZf39/VAqlXhOnoODg7CTs4bdsXr9xXTyTlYuqRXUnB7PExMTmJ2dZfNMdw/tkI54nsc/OdtNDSsgkJoAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def bubbling(self, Face):
        Area_Arc = [Face.GetArea() for i in Face]    # 面积列表
        # for循环排序
        for i in range(1, len(Area_Arc)):
            for j in range(0, len(Area_Arc) - 1):
                if Area_Arc[j] > Area_Arc[j + 1]:
                    Area_Arc[j], Area_Arc[j + 1] = Area_Arc[j + 1], Area_Arc[j]
                    Face[j], Face[j + 1] = Face[j + 1], Face[j]
        return Face, Area_Arc

    def RunScript(self, Faces):
        Faces, Area_Arc = self.bubbling(Faces)
        return Faces, Area_Arc


# 计算Surface面积
class Surface_Area2(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_面积取值", "Surface_Area2",
            """Breps求面积：面积除以divisor，保留decimals位小数；""", "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("9ee46870-e5b6-4d61-a7af-0ffef80f46e1")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Breps", "B", "Brep/Surface物体列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Divisor", "D1", "除数，默认百万1000000")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Decimals", "D2", "保留小数位，默认三位")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Area", "A", "面积")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAQ7SURBVEhLrZVLTFtHFIbNo1kUUCOKBAuisAmbUqUrJNYIVFKBhISQsmhaQGpaIECJAilFpUgNsKECqiQEFpVCbIyBNq3aFVKzSFzaAAaMX9cYXz9wBRiXh7F9sbH/nhlTYxLSR8hIv+7c0Z3/mzkz51zZgkl8d9m+1jOrFV65mK/MYLb3h8MRbGy4X7mYr8xotnWxF0EQYDQaYTAYYDyF+HzyYX7MNwYwmgRYRCdEhwui/RSi+cyH+cUBNmAwmeGT9gFEaGvhlxabz3yYH/MlgDUG2PMH6IOjFgwGueJb9D0SfTmpEWTX5z8E8B1EAUZhGdu7Xh47nU4Ht9sdA7hcLj5msVgg7QdhFl1Ytjp4KOIlrDixtb0HHy30OYDFaoPD6UJGRgYSEhJQV1d3uCSguLiYj71z8SKCoQP8PKXGfcUEFGPfxaSa/BFf3Poacwt6HBxE4gCmI4DdsYqzZ9+ATCZDfn4+N/d6vcjMzORjeW/lYT8Ygvr3eXw7Mor7D+QkBZd8VIVPrl3H/KIWoVAYBuMLAG+mpyMpKQnp9PT5fDw0zDw5ORlv50UBT37T4IF8FKMKOUnBpRpT4dqnLQRYOg7QxwFsDifS0tKQR0YsJHq9HhMTE9w8NzcXuRcu8DNggBECKAigIHOmMQ5ohWZBS+d2cDJAtDtx5sxrqKysREpKCuRyOdra2pCTk4OioiLknD+PAF3Bx9NzUChVZKo8BmggwNz8Ivb3QwQ4zINnAQkJMjQ1NfFd1NTUoLCwEGVlZaioqMC5c9kcMD2zgDt372Fo6B4mJye5Hj784d8BVpuDx7ujowPV1dXIyspCamoquru7cfnyZWRnZ8MfkPBUo8P7Vz5EY2MDent70dzcjNbWm6hvugHNvBaSFPxnQGdnJwYHB3mfaWpqiu8gHnDlgyp8fPUqqqqqUFJSgkuX3uOHfALAEgWsEEC0c8P29nao1WreT0xMhMPhQGlpKQewJGIhujs4hIGBPnwzMID+/j7cuX0bdQ3XMatZQCBApeJZwMqKiGWLlZvW1tbC4/HwPgtRJBJBQUEBHfzr2KMy8CvlwYhinO7+GL//CuU4xsa/R31jC2ZmNfD7pTiAMQoQzBY4V//g5kqlkpcIFtuenh7e7+vroxv1GQeMqH5CS1snPu/4inSLq/3LLnxUfwNP57SUP1SL/gYscYAbOhrY9Gzx7A2FQtje3uZ91o71d3YwvyRQKLRUFnRxWsIslYm19U14/tx6HqBnA24PdsiAGb5YWxQCH6RAgGLtPyaJ5PXuYn1jM+rHAIt6c9cu1RsThYjtQJIkqognGf83sQWu00JjAKtjreuXR4/w+IkaM7RtdmBW2yqEZfHlZBFhEKxHIWJ/NHaQLN2Hh4dRXl5O19IOk8lEMv5/0f+YzY39k3WmlX693kA5IGJ6epqK2yRsNju/puyD0ygcjuAvEHdPWuUdFWYAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Breps, Divisor, Decimals):
        # 初始化参数
        divisor = Divisor if Divisor else 1000000
        digit = ".%uF" % Decimals if Decimals else ".3F"

        # 计算
        Area = [format(Breps.GetArea() / divisor, digit) for i in Breps]
        return Area


# Surface中心面
class Surface_PLA(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
           "ZY_面_Plane", "Surface_PLA",
           """根据面的点序生成Plane,Indexs下标顺讯决定Plane的方向.""", "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("e595f6f2-245f-452b-b117-2ff864c578dd")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Surface", "S", "参数Brep、Surface。")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "Indexs", "I", "Plane生成参考的点序 默认：【0,1,0,3】注：每两个点为一组向量，第一个点为两点向量终点")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "PLA", "P", "生成Plane")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANJSURBVEhLvZVJT1NRFMdZEvgMbFgRVnwJEr4AKzVRogkuKImEsczVytalxoCKtBTaMnRQZLQ1dIYyFNrKkEaNhGihdB7g7z23vNqHhQUQb/JPX17/9/zOucN5RWVlZV9KSkpwUZWVlX6FQjFwE+n1+oEiClZdXY2ampqcqqqqUFpaCma4kcxmMziAgpaXl4MG/RYXF/MqBofeXE+DQ3g3PAyDwfAXkD8EwOb2zrW05dvDp3kTJiYnr67gJmN1zQO1Wp0F0JpTUEH0jvYglUpxJRJJBI9PCur30QlOwtGcl0TDubIGjUaDooqKCj8FvKja2lokk0lu3g98R69MDtmz53gqHxBJ2tULlXqK+8gvzHG4zgFK5Yhco9HC69/lfwimfPPufgBt7R2QSqXo6uwUqanpCd4rVNyXP0cM0J4Dzs7YciREoncEkHZ2obu7Gz09PSK1tLRAMTrGg+bmsOFwuf8zYNu3g7PTU8TjcZHo3c7e5YBWBhhRZgG5OSwpu7MA4DQPQM9kpPHtxwF6evtYwN7rA7a8X5HJZBCLxbgcDgeWlpZgsVgwOqbG/Qd1aG5uRl8fgf4FUC7CXErO7lwtDKAMgsEg1tfX4fV6cXDwE8YPM2iQNKKxUYL+/v4CABXPOh9gcxQApNNpbgiFQpidneW9xGT6jJevXuPO3XuQSBogkxUGUNBoNMpFiV4ATMCz7ee3kAxUgdPphMvlwu7uDtTaKdQ9fIT6+sdo75CipbUtJwmrbPDtCAdEIhGudDrFACtiwOaWj18SMhDAZrPBarViY2MDH2dmMTyiwsS0ASusx9jYBgpatrn4AYnFogiHw1ypVBJWewFAIhHnBgLMzc3BaDRiYWEBOp0OZpMJfp+PnxbKUFCGLSvNC4VYTzrJKsnugtXuEgM2PF62wTFuODw85Evkdrvh9/tht9vh8Xj4xtMhoD26SuSxsMqoBXGAlgHWN7d5mYKJlmd+fh6Li4u8GqokEAjwJTw+Pr5SdFAsNqcYIFQgAKjsbPNKIHXexCKRMEIsgOC5TLkK2OnMAVxuD4JHIRwc/rqxguwbYV62Q5sFKOV6vQ5K1ThU49pbk5I1QIpLgBf09dfppjE9PXVronhmsxl/AIqlHEPE5LaXAAAAAElFTkSuQmCC"
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def Point(self, pts):  # 获取所有点坐标信息
        for i in pts:
            yield i.Location

    def Count(self, num1, num2):  # reduce调用+方法
        return num1 + num2

    def Vector(self, PTS, Index):
        return [PTS[i] for i in Index]

    def RunScript(self, Surface, Indexs):
        if Surface:
            pts = Surface.Vertices     # 取顶点
            pt = self.Point(pts)       # 惰性取值
            Pt1, Pt2, Pt3, Pt4 = next(pt), next(pt), next(pt), next(pt)

            Cx = reduce(self.Count, [Pt1[0], Pt2[0], Pt3[0], Pt4[0]]) / 4
            Cy = reduce(self.Count, [Pt1[1], Pt2[1], Pt3[1], Pt4[1]]) / 4
            Cz = reduce(self.Count, [Pt1[2], Pt2[2], Pt3[2], Pt4[2]]) / 4
            Center_PT = rg.Point3d(Cx, Cy, Cz)

            PTS = [Pt1, Pt2, Pt3, Pt4]
            if Indexs:
                pt = self.Vector(PTS, Indexs)
            else:
                pt = self.Vector(PTS, [0, 1, 0, 3])
            PLA = rg.Plane(Center_PT, pt[1] - pt[0], pt[3] - pt[2])
            # return outputs if you have them; here I try it for you:
            return PLA


# Brep炸开
class Brep_Data(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
               "ZY_炸开Brep", "Brep_Data", """将Brep炸开，获取点线面。中心点坐标系，Brep的ID""",
            "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("d4bc9a70-0c2d-4646-82d9-c38c58c9ffff")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Guid()
        self.SetUpParam(p, "Brep", "B", "Brep模型.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = GhPython.Assemblies.MarshalParam()
        self.SetUpParam(p, "Index", "I", "中心点坐标系下标-根据Brep点序输入；"
                                         "默认[0, 1, 0, 3].")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Point()
        self.SetUpParam(p, "Point", "PT", "顶点.")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "Line", "LE", "边线.")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Surface()
        self.SetUpParam(p, "Face", "FE", "面.")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Plane()
        self.SetUpParam(p, "Plane", "PE", "中心点坐标系.")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_String()
        self.SetUpParam(p, "GUID", "ID", "Brep的ID.")
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
                self.marshal.SetOutput(result[2], DA, 2, True)
                self.marshal.SetOutput(result[3], DA, 3, True)
                self.marshal.SetOutput(result[4], DA, 4, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAKmSURBVEhLzVbfS1phGD43wXYzlpbWHLtLdiH9BSHdbzD6E7zZTQtBImoUJAsvPrVkohANDJQlVv4A+7E5lErJ0Qz8wUrLEVPqIijxpkjw2fnejC2G1NZh7IHnnI/3e9/znO877/t+R6jVas/q9TqrVCqsv7+f9fT0MK1Wy3p7e/+YPI7HDw4OsrOzM8afK4gXx/n5OYaGhjA7O4t4PI7N5GeRyd+5uXkjNzY2MDMzg5GREXAIh4eHbHh4GJlMhgxSYXt7G2NjYxB0Oh1bXFy8tNaqCDgNeP3yOcZfvcD4QIPimNvm7QPARYVcV1dXMT093ZQ7Ozvwer0Quru7WaFQoKCv624oH7agtV2FduV1yhQqtD1oQfrTO/Ll2xEIBJpyd3cX2WwWgkajYcVikYISITsedcjR1aWGWn2dXSI7FXLE5q3kexvwbaIV7O/vkyEZduJxZ3MBlVKOdb+NfG+D/1+gXC7DbrfD4XDA6XRicnISW1tbjVkJBNxuN2XK0dERkae60WhszEogMDExgYODA+RyOSTFQuQFa7X+TII7CbhcLng8HhovLCxQF6hWq9IJRCIRTE1NQexl4IXKBSUV4LDZbOBFenp6CrHlkM1isdCd484C/M3NZjNisRjW1tbg8/lgMpkasxII8I+6srKCYDCIUChEgjybrnBngZvw7wUSwbdQtrc2FVC0yRD1mcn3NkilUpcCV930e3oJmif3IZPJ0CF2zl8pl8vwVHUP374EyJfXwOjoaFNGo1HKMGrXVyvgKCZ9WHKN44P7DT56GhTHSy4jCon3oked/EqlEh0qzXh8fIx0Og2hr6+PLS8vU5DUmJubgyA2KGYwGKgzSol8Pg/x7wL0V8GXq9frEQ6H6ajje/c33Nvbo+3x+/30vJOTE/wAhPiD+YvdyqwAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def Count(self, num1, num2):  # reduce调用+方法
        return num1 + num2

    def Point(self, PTS):  # 点坐标信息
        for pt in PTS:
            yield pt.Location  # 惰性生成

    def Cenpoint(self, PTS, indexs):  # 中心点 坐标平面
        PTS = self.Point(PTS)
        PT1, PT2, PT3, PT4 = next(PTS), next(PTS), next(PTS), next(PTS)

        coord = [reduce(self.Count, [PT1[cr], PT2[cr], PT3[cr], PT4[cr]]) / 4 for cr in range(3)]  # 重点坐标
        Center_Point = rg.Point3d(coord[0], coord[1], coord[2])
        PTlist = [PT1, PT2, PT3, PT4]

        PLA_pt = [PTlist[pt2] for pt2 in indexs] if indexs else [PTlist[pt2] for pt2 in [0, 1, 0, 3]]  # Plane点排序
        Plane = rg.Plane(Center_Point, PLA_pt[1] - PLA_pt[0], PLA_pt[3] - PLA_pt[2])  # 点- 两组向量做plane

        return Plane

    def Module(self, Brep):  # 面 边线
        Linelist = Brep.Edges
        Facelist = [i.DuplicateSurface() for i in Brep.Faces]
        return Linelist, Facelist

    def RunScript(self, Brep, Index):
        if Brep:
            sc.doc = Rhino.RhinoDoc
            GUID = str(Brep)
            Brep = Rhino.DocObjects.ObjRef(Brep).Brep()
            Point = Brep.Vertices

            Plane = self.Cenpoint(Point, Index)
            Line, Face = self.Module(Brep)

            ghdoc = GhPython.DocReplacement.GrasshopperDocument()
            sc.doc = ghdoc
            return (Point, Line, Face, Plane, GUID)




import GhPython
import System


# 插件信息
class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "ZY_Brep"

    def get_AssemblyDescription(self):
        return """欢迎使用此插件"""

    def get_AssemblyVersion(self):
        return "0.1"

    def get_AuthorName(self):
        return "子夜"

    def get_Id(self):
        return System.Guid("96aa2301-c437-4e3f-b2f1-253a0679d723")