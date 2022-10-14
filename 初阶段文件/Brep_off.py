# -*- coding: utf-8 -*- 
# @Time : 2022/4/18 9:48 
# @Author : 子夜
from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import ghpythonlib.components as ghcomp
import ghpythonlib.parallel as ghpara
import ghpythonlib.treehelpers as ght
import rhinoscriptsyntax as rs
import Grasshopper, GhPython
import Rhino.Geometry as rg
import System
import Rhino
import math


class ZiYe(object):
    def Move(self, Obj, Vec):  # 移动
        Objcets = []
        for i in range(len(Obj)):
            Objcets.append(rs.CopyObject(Obj[i], Vec[i]))
        return Objcets

    def PolyCurve(self, PTS):  # 折线拆分成线段
        Curve = []
        for i in range(PTS.PointCount - 1):
            Curve.append(rg.Curve.CreateControlPointCurve([PTS.Point(i), PTS.Point(i+1)]))
        return Curve

    def CSurface1(self, PolyLine, Line, Vector):  # 生成偏移曲面1
        Suface = []
        if len(Vector) == 1:
            for i in range(len(Line)):
                Suface.append(rg.Surface.CreateExtrusion(Line[i], Vector[0]))
        else:
            for i in range(len(Line)):
                Suface.append(rg.Surface.CreateExtrusion(Line[i], Vector[i]))

        DaMian = rg.Brep.CreatePlanarBreps(PolyLine)[0]
        for i in Suface:
            DaMian.Join(i.ToBrep(), 0.02, True)
        return DaMian

    def CSurface4(self, PolyLine, Line, Vector, Distance):  # 生成偏移曲面2
        Suface = []
        for i in range(len(Line)):
            Suface.append((rg.Surface.CreateExtrusion(Line[i], Vector[i])).ToBrep())
        Suface.append(rg.Brep.CreatePlanarBreps(PolyLine)[0])

        brep = []
        for sf in Suface:

            brep.append(rg.Brep.CreateOffsetBrep(sf, Distance, True, True, 0.02)[0])
        Breps = [i[0] for i in brep]
        Brep = rg.Brep.CreateBooleanUnion(Breps, 0.02, True)[0]
        return Brep


# 曲面偏移
class ZYBrep(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
               "ZY_偏移曲面", "ZYBrepOff", """根据折线生成偏移曲面。""", "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("ee58788c-4219-47bd-8935-e981aedf11a6")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Brep", "B", "Brep")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Vector", "V", "各分线段各自的偏移方向")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Distance", "D", "偏移距离")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Brep", "B", "偏移后的Brep")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOrSURBVEhLrZVdbFNlGMdrNOhwQHRmusIkjLDqIlGJkWsTboBLbk28MMELv4goX0qIFwbjpVwQDOvHaTnlewvdN+go9Wzrx7q1sLXbuinxA0Lmuq4fO6c97d/neU3LulW2LHuT/8U5fZ7/73mf93lPDWdtrn3SpfYfzjbLay72Ndgv3jhz544HbW1tay72ZcD3LlcbnE4nJEmC2WyBxbJ6cb7dLgk/9i0B7HY7OnpuwzsYxoB/eNXifFfnLeFXBmg2mzESncRarGBolHZiLgeYaXuhe1ERkM1mKyqXy5V+z7H0PB4+mim9Y/Hy0S64XWUAi8VaAmiatkT5fJ4MNMQmp0QMr2++PY1XjK/i3HmbeOY4Xr7B0MoBqqqKd6lkAoryK660duG24oenP4AdpiY8/ZQBH338uYhZFjB8N0I/F4Qpq5gQi8Vwo70bwdE/0NLRC+OWragzboaxrg61tbU4fPRrEVcsxhtYKUCdh9/vx3lHK845b+L0jxKapctkbkR9/RaYTCYB+OKrE8J4eUA4gkIhj/n5eTrQLB48fISfPQGM/5XG/gMfwGAwYFNNHUyvNZF5IxobG8sAnFcoFDAQGK4MGAqP0mHqyGQyKNChRsan8P6Hn+LgJ0dQtX6DAFRvfAmvN+0k8x1LAJzHw8D3YVkAlYKx2G/CdKE2vvAyAd4QO2hoaED18+tx6PCxFQJCI9D1HNLptNhBdGIKz1ZVVwRsb9iGN9/ahff27MWXx0+J1nCeruvo9w9VBgQJkNOzSKVSyNMl4hYtBlRvqoVxcz1qal7E5ZYOjN2fRm9/WFTPeXwZ+30MsBYBrSXA4PA9cZmSySR0CoyMTS4B7Hz7XRw7+R0OfnYC3X1ROK71iEnjCWIA5/f5gv8P0Chwbm6OPgUaRqOxJYBd7+zGgxkVXUoEVvk6hoIBZKg1XBTnaZqKPm8lgNWKAAFUGrVEIiEAd0fG8cy6KmG8bbsJJ+nTcOjIKSi+EH4yy5iYmBDjzMacw1Lp7ijeQeEnALaFgGAYKvVydnaWQBlM/f4n1j3333hK8lUxKZP3/0ZnVzfiM9OiLRy7UJyvDDwBwIdVDOap6Oz5BWabjHh8lipN4J/paVEptyQej5eZszhfGQgsAMjlLdI02jL3U/Q0KarmlUqlxXOSDjKZTD2OWSTOV7w0RYsBDocD11rb0X3LTVX3rlqcf7XFhQvkVwZwyjIc9Ddns1kh2WyrFuc7HHbI5FcEnHG7PeJhreV2e/AvvVnnqkBHQSwAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Brep, Vector, Distance):
        Ziye = ZiYe()
        if not Distance:
            Distance = 3

        if Brep:
            Linelist = [cr.EdgeCurve for cr in Brep.Edges]

            if Vector:
                if len(Vector) == 1 or Distance > 0:
                    DaM = Ziye.CSurface1(Brep, Linelist, Vector)
                    Brep = rg.Brep.CreateOffsetBrep(DaM, Distance, True, True, 0.2)[0][0]
                elif len(Vector) > 1 and Distance < 0:
                    Brep = Ziye.CSurface4(Brep, Linelist, Vector, Distance)
            else:
                Brep = rg.Brep.CreateOffsetBrep(Brep, Distance, True, True, 0.02)[0][0]
            Brep.MergeCoplanarFaces(0.02, True)
            return Brep


# ZY_压顶板实体
class ZY_YDB(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
                                                           "ZY_压顶板实体", "MyComponent", """压顶板实体插件：
    适用：直线压顶板。接口处需要延伸出一个接口。""", "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("ddf1019d-a9fd-40a8-859d-3762878601c7")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Brep()
        self.SetUpParam(p, "Part", "PA", "整体实体大面")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "Curve", "CE", "截面线（最终线段）")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Distance", "D1", "截面线偏移距离")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Plane()
        self.SetUpParam(p, "PLA", "PA", "截面线偏移参考Plane")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "Index", "IX", "需要延伸的线段下标")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Re_Sta", "RS", "延伸的线段起点缩短距离")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Re_End", "RE", "延伸的线段终点缩短距离")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Vec1", "VE", "延伸线段的延伸向量")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Distance2", "D2", "偏移大小")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Surface1", "SF", "延伸面")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Breps", "BS", "未结合的Breps")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Brep", "B", "偏移结合的Brep")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        p5 = self.marshal.GetInput(DA, 5)
        p6 = self.marshal.GetInput(DA, 6)
        p7 = self.marshal.GetInput(DA, 7)
        p8 = self.marshal.GetInput(DA, 8)
        result = self.RunScript(p0, p1, p2, p3, p4, p5, p6, p7, p8)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)
                self.marshal.SetOutput(result[2], DA, 2, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANUSURBVEhLrZXJTxNRHMdHxUQTE+XiSqJ/gje9eFFcIDGA8YDRxLgQdwUEo5WDiHFXYlArYDtdBxHCYluBAukyULaKyK4iQTHhYuLCVpi2X997NYFmppAgv+R7eL/tM+/3Zt5wj9TmeFOx7b5aIyy6DKQvV8ALeaIowmq1LrrcbhFcPi/cpYuiIgEGvR5aLQ+eX7hovdFoJP2KYLFYZwAG4qypF9H2vhut7zoXLFpfabMTiCEcoNHq8HlwGIthntZ2shNtOEDL69D3aZAlTE9P/5OEacmPQMA/yxeSJEnwTUkIBgNhfmpiUxsbVxiAJ4Dej19YgiSFEvsHvkJsbsfv0QmyCiLgJ0DahDT99WccjoY2DA2PEEiQuPzwkzg10TMPYGLSh+8jP+Bwe1Btr0djsxfDZP1ndBxTU1MM6CWzrrbXod4hkp0P4efvMYyPT7L6iICe/hBAX2zB7cf5eFGox9btu5B14w5KK2xISc2Gq6kDD54aUFZpQ3zSYRxIPobi0gpk33uGsxk5rL6BjEgnB+gJYIAlvK60I+3qLRw5fga74xIRn5CME6cvITE5BbWuVjzJN+N8mgpx+w9id3wSDh09haMnzyHlwjVyXsEQQDcH4E2NiNy8ArIDHhqdCYVaA5EeN+88QZ3ohU6ogDpfg5e8kYnmqQs0uP1QDckfYCNSBHT3fWaAkoq3iF4bA47jwhW1irwhXlxIV8ljRDv3JrB60dM6N6CUANZt3CxrELViNdweL1Izs2QxqlgyTmrKAJ0eXb0zgPWbtsgaLF+5Bu7Gtn+ApbJ4bFwSq3c3UoBOCfCJJZSU2yICXKQ4NfM6WSsBQjtwN7YoAzp7PrKEuQDOhvkBroYIgA/dIcDrssgAh9iC1Iz5AM2RAP0sge5gQ4wCgByyw92MdHYGS2TxXftCb5EzEqCjq48l8KYSLFsRLWvAcctR5/SQD/CcQozDth17WL1TnANAL7oaRxMuXlYh7UrWjMhTZ6hyyAX4DbnPeXYOs+OXMlR4rhFYvVNsigAgZzAxOQmfz8eeRMnGxsbY7alk1E8vSjpGGcBkNqO03AJrVS0sb+0LlrWqDsUl5TCbTeGAIkGAyWSEwaD/b9HmAunHAC/4V3n0708Xiy2XS8RfYjBLSibHeVUAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def offset(self, cur, Dis, PLA):  # 偏移线段，返回两组线段（偏移线-组面线）
        Reline, SurLine = [], []
        for CE in range(len(cur)):
            PCL = cur[CE]
            DIS = Dis[0] if len(Dis) == 1 else Dis[CE]
            line = rg.PolylineCurve.Offset(PCL, PLA, DIS, 0.01, 0)[0]  # 偏移
            Reline.append(line)
            SurLine.append([PCL, line])
        return Reline, SurLine

    def BrJoin(self, Brep, Surface):  # Brep结合
        for sf in Surface:
            if sf.GetType() == rg.Brep:
                Brep.Join(sf, 0.02, True)
            else:
                Brep.Join(sf.ToBrep(), 0.02, True)
        return Brep

    def TilrExend(self, Curve, sta, end):  # 线段延伸或缩进
        CurveSta = rg.CurveEnd.Start
        CurveEnd = rg.CurveEnd.End
        if sta:
            Curve1 = Curve.Trim(CurveSta, -1 * sta) if sta < 0 else Curve.Extend(CurveSta, sta, 0)
        else:
            Curve1 = Curve
        if end:
            if end < 0:
                Curve1 = Curve1.Trim(CurveEnd, -1 * end)
            else:
                Curve1 = Curve.Extend(CurveSta, end, 0)
        return Curve1

    def Brep_Bool(self, Breps2):  # brep结合，
        Brep = rg.Brep.CreateBooleanUnion(Breps2, 0.01, True)[0]
        Brep.MergeCoplanarFaces(0.002, True)
        return Brep

    def RunScript(self, Part, Curve, Distance, PLA, Index, Re_Sta, Re_End, Vec1, Distance2):
        if Curve:
            if Distance:
                Reline, SurLine = self.offset(Curve, Distance, PLA)
            else:
                SurLine = Curve
            Surface1 = []
            for SL in SurLine:  # 组合先成面
                Surface1.append(rg.Brep.CreateEdgeSurface(SL))

            # 缩短线向量成面
            a = Reline[Index]
            Curve1 = self.TilrExend(a, Re_Sta, Re_End)

            Surface3 = ghcomp.Extrude(Curve1, Vec1)
            Surface1.append(Surface3)

            Breps = []
            if len(Distance2) == 1:
                for sr in range(len(Surface1)):
                    Breps.append(rg.Brep.CreateOffsetBrep(Surface1[sr], Distance2[0], True, True, 0.02)[0][0])
            else:
                for sr in range(1, len(Surface1)):
                    Breps.append(rg.Brep.CreateOffsetBrep(Surface1[sr], Distance2[sr], True, True, 0.02)[0][0])
            if Part:
                Breps.append(rg.Brep.CreateOffsetBrep(Part, Distance2[0], True, True, 0.02)[0][0])  # 偏移
            Breps2 = ghcomp.BrepJoin(Breps).breps  # 结合
            Brep = ghpara.run(self.Brep_Bool, [Breps2])
            # return outputs if you have them; here I try it for you:
            return Surface1, Breps, Brep


# 圆弧铝板实体
class ArcPanel(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_圆弧面实体", "ArcPanel", """圆弧铝板实体生成，参数较多，不易调试查看，
请将所有参数连接查看效果""", "ZiYe", "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("32aeca57-6e14-4773-82ac-9458b6ce3421")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "PolyLine", "PL", "偏移后的面折线, 生成大面")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "Up Down", "UD", "横向线段(上下) ")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Vect1", "V1", "横向线段移动向量")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "Left Right", "LR", "纵向线段(左右)")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Vect2", "V2", "纵向线段移动向量")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Rotate", "RT", "纵向线段旋转角度(不用转为弧度)")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Plane()
        self.SetUpParam(p, "RPLA", "RP", "旋转依赖的平面")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Distance", "DT", "所有面偏移大小")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Surface", "S", "各线段最终生成的面")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Brep", "B", "面偏移生成的面板实体")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        p4 = self.marshal.GetInput(DA, 4)
        p5 = self.marshal.GetInput(DA, 5)
        p6 = self.marshal.GetInput(DA, 6)
        p7 = self.marshal.GetInput(DA, 7)
        result = self.RunScript(p0, p1, p2, p3, p4, p5, p6, p7)

        if result is not None:
            if not hasattr(result, '__getitem__'):
                self.marshal.SetOutput(result, DA, 0, True)
            else:
                self.marshal.SetOutput(result[0], DA, 0, True)
                self.marshal.SetOutput(result[1], DA, 1, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAALzSURBVEhLrZVNS1tREIaDLkRQEUFQiCAY/AduxD/QvejOhcugC78QEfeCuoobFzWJpkmxLWKNxtK0obnxWm0VUo1J1KZCdir4Ec2XSd6eGdu0sSemaA683CR35n3unZmTo5l5bntmfb0yPmO0Fl3kq7FarQZFUWC324suRfGAAOP0xWazYm7ODKPR+GTNz88LP5uArPwB0I9r711QN3ew/vnro0X5S/Y19ssBzM6acPQjjGKsrW2v8JvNBRiNJgQOQxyQTCaRSCT4898rk8lkdX9RPOXR2tja4VLlAkwCcPCdAyg4lUphYWGBmxUKhXB2doZIJIKbmxtcXV3h5OQEgUAAFosFbrcb6XQ6+1Dq5jYDlh8C0Gpra4NGo0FZWRlqa2vR0NCAxsZGaLVa1NTUoKSkhO+Pjo5yfEGAPygA4vV/B/b19aG6uppN8qmurg4mkUtli8fjnFcQQLW8vr7G2NgYhoeHMTIygv7+fvT09ECv16O3txeDg4P85AMDA5ienuaSFgCYsR88QkbUkoLPz89RWVnJT0lXKotOp0NzczOamppQX1+P8vJyvt/a2srGBKA3oXGVAwKHSAtzalg4HEZVVVVOOfKppaUlWyLKLQig5fP5UFpaKjW8L3qraDTKvXsQ4PMf4vb2lgGqqkrNZKJy0RhT76i8no08gD3/QXazrK6uSs1kqqiowPHxMZunxAN6Nr6IyZIB9oPZEaUNJDOTifaD1+vl8iRFvkclgOlfwK4vmB21qakpqVk+uVwuzqN8Rd2SA775AojFohw4MTEhNconp9PJkxSLxaCsSwAmAuz5xTTc/decnp7C4XBgcnKSd3RXVxc6OjrQ3t6Ozs5OdHd3Y2hoCAaDQRwsCi4vL1k0Te71zTyA3TsAbTKC0Kb7n0WTd3FxwXkPA6gHibgwjzxacdFkt6zJNDWLb1fEqfYRjncfHi06FV+9WcIL4ZcDEFdYxDFnNpsx9wRRPpmT3y/AS4NbNGl52V50fVI8+AkYhmYwDNzYmwAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    # 对偏移后的面进行切割
    def Tile(self, Q_surface, B_surface):  # 1.PLA平面，2.被切割面
        ud_surface2, PLAS = [], []
        for i in range(len(Q_surface)):
            cenpt = ghcomp.IsPlanar(Q_surface[i], True).plane  # 引用内置IsPlanar电池提取中心PLA
            PLAS.append(cenpt)

        for surface in B_surface:
            if surface.Trim(PLAS[0], 0.02):
                trsur = surface.Trim(PLAS[0], 0.02)[0]  # 平面切割
                trsur = trsur.Trim(PLAS[1], 0.02)[0]
                ud_surface2.append(trsur)
            else:
                ud_surface2.append(surface)
        return ud_surface2

    def OffUnio(self, Surface, Distance):  # 偏移曲面 Brep结合
        Brep = []
        for be in range(len(Surface)):
            if len(Distance) == 1:
                Brep.append(rg.Brep.CreateOffsetBrep(Surface[be], Distance[0], True, True, 0.002)[0][0])  # 偏移
            else:
                Brep.append(rg.Brep.CreateOffsetBrep(Surface[be], Distance[be], True, True, 0.002)[0][0])  # 偏移
        Brep = rg.Brep.CreateBooleanUnion(Brep, 0.02)[0]  # brep结合
        Brep.MergeCoplanarFaces(0.2)  # 消除参考线
        return Brep

    def RunScript(self, PolyLine, Cruve1, Vect1, Cruve2, Vect2, Rotate, RPLA, Distance):
        Distance = Distance if Distance else [-3]
        if Cruve1 and Cruve2:
            # 生成边框延伸面
            ud_surface = [rg.Surface.CreateExtrusion(Cruve1[cr], Vect1[0]).ToBrep() for cr in range(len(Cruve1))]
            lr_surface = [rg.Surface.CreateExtrusion(Cruve2[cr], Vect2[0]).ToBrep() for cr in range(len(Cruve1))]

            # 旋转面
            for i in range(len(lr_surface)):
                angle = math.radians(Rotate[i])
                lr_surface[i].Rotate(angle, RPLA[i].ZAxis, RPLA[i].Origin)

            ud_surface2 = self.Tile(lr_surface, ud_surface)

            # 大面 集合
            BigFace = rg.Brep.CreatePlanarBreps(PolyLine)[0]
            for sur in lr_surface:
                BigFace.Join(sur, 0.02, True)
            Surface = [BigFace]
            Surface.extend(ud_surface2)

            # 偏移
            Brep = self.OffUnio(Surface, Distance)
            return Surface, Brep


# 孔 - 圆柱
class ZY_Cylinder(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
           "ZY_圆柱开孔", "ZY_Cylinder", """在指定坐标原点生成开孔圆柱""", "ZiYe",
           "Brep")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("d8360a85-40c8-4877-8590-048bcd679cc5")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Plane()
        self.SetUpParam(p, "Plane", "P", "指定Plane，以Plane为圆弧的中心")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Number()
        self.SetUpParam(p, "Radius", "R", "圆柱半径.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "CriVec", "C", "圆弧延伸向量，决定了圆柱的长度方向.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Move", "M", "若需要生成多个，输入移动向量.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Cylinder", "Cl", "切割孔--圆柱体.")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        p3 = self.marshal.GetInput(DA, 3)
        result = self.RunScript(p0, p1, p2, p3)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOzSURBVEhLzVZbT1NZFO5vIJHLGw+E8AOIPiBQeKNCnNECSglQMG3thRaoaDtDgYChPRlhKJQSCgZSERsvOMLUQNQKqDRSriWUQJjIIJCQISE8CAyXz7N3D9YES6LpJPMlq91rnb3Wd9bu2muVt7+/f+Ho6IhZW1tjhEIhExMTw8TFxf2wxMbGMnl5eczW1hZD4vLYD8vu7i7KysrgcDjg9Xrh8/kwNzf33UL8pqenYbfbUV5eDgLexsYGo9frMTs7Sw2hwujoKKqrq8HTarVMT08PZw4tbDYbeKmpqczk5CRnCi2Ghob8BFNTU5zJj/X1dTQ2NqK9vZ1KS0sLmpub6bqjo4N+E91qtX7Rm5qasLm5yUXwY2Rk5NsZkAd8Ph8lahVKNCqwexAVFQV1MaurFVApFThzJhwCgcC/h5Xk5GT6A3+N4eHhbxOwlYXMzExYO+7DYrNDoZDj0aOHyC+U4N5DJ66I8tD37BkKCgpwt/sx7phtyM3N5bwDCEpAIJaoUNjyNyTWv/CLoRpvXc8hkDRA5wQE4tvwvHuJ4lIdlJ3/QPSbF6riUs4zgFMJrubLcLHOB6HRC+2tXzH8oh8JOXWQsQV3PqsC798MQqLQIuf3DxBUuCG9Xsx5BnAqQU6BDJeMPmSZvLjBESSK6iB/ACRl+wmkSi1yGz8g3fB/JBCJ5fjJuAgh48NNvQHvXj9HgsiE6w4gMbsSE+5XkKnKkWP+CIHBA5lcw3kGcDpB/jX8XOFCVuULqNQleOKwIzlbD0nbCviXS/Dn0wcQX5NDVOfGBe0fkEjlnGcAQQk8Hg8iIyMgk0pRWCjGuXNnac2npPChVCqReD4B6enpiI+P/7InPDwci4uLXAQ/ghIMDg4iOjqarnd2PqG2thb9/f3o6uqiNoulGQMDA6g0GKh+sP8vIiIiMDExQfVjBCVwuVxsBpF0vbe3B51Oh76+PtoyCEwmE32J0lJ/7R8cHCAsLAwzMzNUP0ZQArfbjbS0NNTU1NAg3d3d2N7epjeX9KiioiKQGUJ6EWn1BjaTjIyMEy0/KIHT6URbWxtaW1vZ47BgdXWVCulR5LjGxsaovrKygoaGBnR2dsJsNtPnX4MSsE3tRDddWlpCVVUVPRIi5EiMRiMNRkjr6+upTuwkC/ISJAt27HIR/KDdNCkp6UQGoQKdBwqFgiGz+L8AmRO85eVlhh2bWFhY4Myhwfj4OK0+3uHhoYVMIrVajd7eXszPz1OyHxFy0cg/C3IiGo2GvUM7+Ax9rTRuGbJ7sAAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def circle(self, Plane, Rad, Vec):  # 根据面生成圆柱Brep
        circle = rg.Arc(Plane, Rad, math.radians(360)).ToNurbsCurve()
        Surface = rg.Surface.CreateExtrusion(circle, Vec).ToBrep()
        Brep = ghcomp.CapHoles(Surface)
        return Brep

    def RunScript(self, Plane, Radius, CriVec, Move):
        if Plane and Radius and CriVec:
            cir = self.circle(Plane, Radius, CriVec)
            cylinder = [cir]
            if Move:
                for mo in Move:  # 移动生成
                    msur = ghcomp.Move(cir, mo).geometry
                    cylinder.append(msur)

            return cylinder




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
        return System.Guid("96aa2301-c437-4e3f-b2f1-253a0679d765")