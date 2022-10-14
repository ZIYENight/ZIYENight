# -*- coding: utf-8 -*- 
# @Time : 2022/4/13 14:12 
# @Author : 子夜
from ghpythonlib.componentbase import dotnetcompiledcomponent as component
import Grasshopper, GhPython
import System
import Rhino
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import ghpythonlib.parallel as ghp
import ghpythonlib.components as ghcomp
import math


# Curve
class PtLine(component):
    def __new__(cls):   # 插件信息
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_PTLine", "PtLine", """点向式绘制直线.""", "ZiYe", "Line")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("61a8337e-8f08-4800-8732-27ef617bc0d8")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):  # 输入端
        p = Grasshopper.Kernel.Parameters.Param_Point()
        self.SetUpParam(p, "start_pt", "PT", "起点---point")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Vector()
        self.SetUpParam(p, "Direction", "VD", "Vector：向量大小")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "BS", "BS", "方向(使用Toggle判断)；True：双向；False(默认)：单向；")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):    # 输出端
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "line", "l", "所得直线line")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        p2 = self.marshal.GetInput(DA, 2)
        result = self.RunScript(p0, p1, p2)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAALiSURBVEhLrZXJThtBEIbniOAtUKSIBILBTiJxDDiYLXmDKFE4JIfcEBeEkGU83pgZjw3ex/u+xn4VDuSSKwcegj9VTXDAHsAmWPrUnu7q+quqq2eky8tLBwBvu9327u7uPgk7Ozveer3uZb8soF9cXKBYLKLb7aLX64nxf2F/5+fnkM7OzmRSQ6VSQalUejLYX61Wg5RIJORmsykmWXUcCoUCyuSoWq2K/zfX2F+r1YLk8Xhkqr8wGId8Po9yuYxM2oCu68LhoE2n04HkdrtlVuINo5LL5VCgKHvdn7AtzsO+8g4c5KAdzwkBLhFvGoVsNis2d9otOOzLeGtbQDIRo4iLQ7aiRC6XSxxyJpMZiauNTTjeL+ON1YJK+areZraNRuNKgE87nU4/CEffajawvrqC11SaUpFLUTC1ZThwIcBdYBjGvXBEzUYdG2t2WBfmUMhzGfKmtteINnU6nTL3bCqVuhPDSFO6NWyur2Jxfhb5LGeTM7W9CQcuBLiGyWTSlFTKQL1WxdbGKiyvXlAmlA2Vysx2EG5jIcAXgy7cEGxUoyg+bK5hfnYGaSOJNJUqHo+b2g/CgUsHBwcyt10sFhuiQPMft9Yx9/I5icWRorqa2d0FXzZpf39f5u6IRCJ94rTIottfPmF25hk9R0kgdctmFLilhQB3yMnJiYAXjhQNqhaCx+1EMOBCLBrB8d/1ceDApb29PZlbKhwOC5JUu+1vP/D563d6z2QQixwjpPkRCul9m1HhuyBNT0//mpycxCBWq1W8xJiQriGo+hDUVASDOhEcCW4SiZ3Z7XY4HI4+FosFU1NTUFVVoGkkoClQFR8906hqYu4huNuEADulTOgLBzFOTEyILBRFuYWqHEE58hGBoTUzotHoP4Gbv2uBQCBgjt9vPj8AH/S9Gfh8vkfjpyD4/IQA15ydXsNzfAb0tXsUXq9XwGWSlpaWfrPDQWw2W/+Qx4UdHx4e4vT0FH8AKqvnuNO+vUQAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, start_pt, Direction, BS):
        if start_pt:
            if BS == True:
                line1 = rg.Line(start_pt, Direction)
                start = rg.Line.PointAt(line1, 1)
                line = rg.Line(start, -Direction * 2)
            elif BS == None or BS == False:
                line = rg.Line(start_pt, Direction)
            return line


# 求线长度
class LineLength(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_求线长度", "求线长度", """求线长度，并保留规定的小数位。""", "ZiYe", "Line")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("c683174a-8426-4e49-9fa3-0d986603bb70")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "线段", "C", "求长度的线段列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Integer()
        self.SetUpParam(p, "小数", "N", "保留*小数.")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Length", "L", "线段长度.")
        self.Params.Output.Add(p)

    def SolveInstance(self, DA):
        p0 = self.marshal.GetInput(DA, 0)
        p1 = self.marshal.GetInput(DA, 1)
        result = self.RunScript(p0, p1)

        if result is not None:
            self.marshal.SetOutput(result, DA, 0, True)

    def get_Internal_Icon_24x24(self):
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANNSURBVEhLrVTLLmRRFK3v8AXeRAwxQCQ1ljAy8AOGBgbMDNpIIkIiEYTqSKs2oNXjFtV1CYkwEIJU6Q7VjY563Fe9H6vP3uWWQqFb7GQN9lnnrHXO3vtei81ms66vr39aWlr6cJCu5bPNNu7z+bBi/4ovKx8L0rUsLCyMfnO4cOq/RODnL/h/BP8LdObi8vd9fnW/FsT5RRAOlweWubm5Uae0iWw2j/cHnX1+3rMlXsAGbg9i8aQwySKdTr+JTCaDXC6HoaEhtLW1wWq1IpFI8BrxWcEnU2lIm98fDIxYgg+mUql/AoUYEFgsFvT393Nuchlhkkim3m9Asbe3h87OTnR0dMDpdPKayb9ikH4kVIpkMsmg8Hq9qKysxP7+PlZXVxEKhXjdjLTY/8xAN+Kifg9C5UCxsbGBqqoqHBwccE5BBvPz85ienobD4eBexhNJYeB924CaZ4rb7XZUV1fj+PiYc+JI7Pr6mktF/ZiammLumYGmx0QpCoJPQbG4uIja2lr4/X7O4/E4g+L8/BxdXV2or69ns3w+J6Yy8bIBHczn81x7ipmZGTQ2NuLq6orzUnEqVUNDAyYnJzEyMsJr9OKiwQIZiC9O1QxBFMRpms7OznjzxMQEmpubcXNzw3ksFmNQ7OzscLOp6RS3t7fFshqxOCRPGQMi6eYDAwMYHBxEa2srwuEwC5SKS5LE4ru7u5zTxegjI76sgaLqgojz13h0dISKigr09PRA13Uul2EYRfG1tTWepMPDQ85NzgSZ6UbssUFU0QRREBgeHuaJaG9vRzAY5EkhEYrl5WXU1NTg5OSEc1p/CjLRdANu04D+epGoWnSXZRkul4trqyhKsdliIFBXV4dAIMA5va4cyETV9HIGOjRN4xubcXp6itnZWf6QSieJ9pUTJ5QxkBCOKIIoGJigIPGmpiZ0d3fzJFE/VFV9tO8pyERRNWGw9WAQCkcFofFhU4Aa3tLSwv2gPycFlczc8xLobFRRHxvchSKCUFmAQM+kue7t7UVfXx/GxsZ4/EjA3PMSaE8kqrxuQIhGo6IfGb45lYbyUv4lFA2kEoM/dxFRtwLxAMpNlK6/DipPSPTURQaituOyvA33pg/SlvxhcG/KkLd38Bc5RMF1fyEJ8AAAAABJRU5ErkJggg=="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def RunScript(self, Curve, Number):
        digit = ".%uF" % Number if Number else ".1F"
        Length = [format(float(crv.GetLength()), digit) for crv in Curve]
        # return outputs if you have them; here I try it for you:
        return Length


# 根据线长排序
class ZYLLenght(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_根据线长排序", "ZYLLenght", """根据Curve的长度进行排序，从小到大。""", "ZiYe", "Line")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("e93bc482-0f62-42b6-bf53-97caa94435bc")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Curve()
        self.SetUpParam(p, "Curve", "C", "需要排序的线段")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Curve", "C", "排序后的线段")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Lenght", "L", "排序后的面积")
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
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAOlSURBVEhLxZXbT1NZFMYbEv4DXiCEF3wxmZg4D8rDxHgjSmIiGi/jAyNGnTgXmakYHCKGKlLLjHHG6JMJMQYTBiqioyYOmZmA1jIRCBm17TmnLVRpeYAEWjic3k77zVq7tFAKatDElXznsvfK/u291tp7Gx4/Gdrp8vot9ucvszW4RKvod7j9FsPz4VdXkwAmJyc/upI0sGFg2GHmH1mW4HQ6P5pkWRaQDMAlKxh57cfoe8j3JoDXYyn50m9qS7fzOC5JWQBMTEzA7fUhkUiSEhSwlCVpjfyfI1o6h5U9+S1Ej0w7fSgeL3jcRYBRxOJxxGIxSJIEh8OBcDiM+HxbWgy9casTP9abYbJcx+VrN3G85iz+6rXjz79tOFj9g/Bxe0eWADyj0Gl24bCG4uJi5OfnY3x8nOYDRKPRjNjON/+Cit2HcPjYSdTUnsUXmyvQ2XUf7Z3dWLuuTPisDNA0FBYWIi8vb0WA+effsOfgEXz93Wmcrr+A7RV70XXvETrvPsDnZVuFTw5AIUBc16Fpc5kVBAIB4RyJRDJia54HHP+WAecF4E73Q1rFHwTYInzcnk8B4CTPzWUDOGGc7LTYmlsIcKA6BfgpDXiAjjv33wGIEUBVMwC/378ioFIAalFLgG2LARvTgCVlqhAxSmWoqrNZAK57jRKfFtvFll9zAFZK8GJAzj5Q3CMU4yhmZxcAY2Nj0CkvHLa02C5aUoBj3xDgjEkAOP6/W+9hPQF4s70FMPPBAN7hywLC4QhmZkIoKioSAJXysZw1Wa6gcv9hATjFgJ17UhttHqDTEhT3IsAkfcgE0LQwQqEgSkpKxEarq6tDU1MTTCYTGhsb0dramgJcuoLd+77C0RNGGOsasW1HpZh9e8ddrN+wGXFawjIAL4VAQ3B6GgUFBTAYDDkqLS0VgIYLLdi+60scqv4eJ2rqsXFTBdrau3DrthVrPitDTIcYLxugeCn+KqYJUFVVhfLy8hwZjUZx4PUPvMDDnqfo6f0Xvc+G0P3oHzgkL1463ejo7sGsOgdJ8WQDJAJMB4MIkvgEzTmiSTw4TyBCB6Iej9I/n08RJHTeoKpQMqFjinwk2b0A4MRyDlSqEq71UChEyZ7JFbVz37sUDIboApsHDP8nmQcHB+FwybD1D+CJrV/cWgpdQKuV7PGJ8cSNZusfMjc0nENfX5+oGq6YAB3TTpdr1XKRMndyn23gqt1uh8/nQ1tbG6xWK6ampkTnhyqZTOJ/lvFWWS2o6H0AAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def bubbling(self, Curve):
        Length = [i.GetLength() for i in Curve]
        for i in range(1, len(Length)):
            for j in range(0, len(Length) - 1):
                if Length[j] > Length[j + 1]:
                    Length[j], Length[j + 1] = Length[j + 1], Length[j]
                    Curve[j], Curve[j + 1] = Curve[j + 1], Curve[j]
        return Curve, Length

    def RunScript(self, Curve):
        Faces, Length = self.bubbling(Curve)
        return Curve, Length


# 指定线段 取顶线底线
class ZLine(component):
    def __new__(cls):
        instance = Grasshopper.Kernel.GH_Component.__new__(cls,
            "ZY_指定线段", "ZLine", """在线段列表中，根据线段Z坐标取出指定的线段（顶线 or 底线）
并统一该直线的方向。""", "ZiYe", "Line")
        return instance

    def get_ComponentGuid(self):
        return System.Guid("4904712b-7881-400e-a4d6-0b53069c48bc")

    def SetUpParam(self, p, name, nickname, description):
        p.Name = name
        p.NickName = nickname
        p.Description = description
        p.Optional = True

    def RegisterInputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_Line()
        self.SetUpParam(p, "Lines", "Lines", "直线列表")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.list
        self.Params.Input.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_Boolean()
        self.SetUpParam(p, "Dir", "Direc", "True-将直线统一为正方向->->; False: 将直线统一为负方向<-<-。默认为False。")
        p.Access = Grasshopper.Kernel.GH_ParamAccess.item
        self.Params.Input.Add(p)

    def RegisterOutputParams(self, pManager):
        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Line1", "Topline", "最终得到的顶线")
        self.Params.Output.Add(p)

        p = Grasshopper.Kernel.Parameters.Param_GenericObject()
        self.SetUpParam(p, "Line2", "Endline", "Script variable ZY_指定线段")
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
        o = "iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAANUSURBVEhLvZbLTxNRFMb9G+AfUBKFGDE+tizZGBITEpduSdwYdiaG4MqwMAGsLS8fsZ3SdgoW8BkBF4D4oFBpS9tpa6el4CO0RoFEHn193nPK9AHixoZJTs453733+93OTOb22PhbzyV3ePXOzJy34uEVvsfmPQFdNpdDMpmseOSErwAoHQnRhEJBBAKBigX5EYQByWQCgeBnqPFviFYgyIf8yDf/C9bWEI4sI5PNAdkscv8RtJ58yC+RWCsFxLCbSuPglUMqldqry6/DdPIhvzxgUQBEoQEWXG68ffcRM7MfOa9+/c5GK6tfseRXRAThExFf+cJ6bHlFzP2AGTGX5seWV4WeRuhztBwQUZeRymRx+cpVnDx9HnVnLuL4qXr03Jd4VzdvdaCm7hyPnRD6tes3WO99IO3Nv4Ca2rNov93N+gFAOBJFKp3Be6cXFquMkdFR3OsZwNOXb3iBaymMR0YLrDYZOkM/LMPPWQ9GVmCxPYHD4cDAw8ewDD1lPQ+gh7wPMP1+ASZJwtCQjG6dHmMvJnjBoi8sdAuG7DIMvf2wDT9j3R+KwWS2wC5b0ds/gEF5lPUDABLoGUy9W4DRJMEujLruFgGfvCE8Ng1Clm3Q9/TBurdTAhgFWLZZ0dM3APO/ADu7KQGYLwOMPh/nBS5vUOhFgHYrfMGoAFhLACOsHzUgwcL2zi6mZudhKgAMRYBnH8A+xvrSPoBkGxHfIAKoRw5QsbW9cwAw8uw1G7k8ijDSAP0Y1ACKCqM5D+hlgEN8LXIIhlUkSwEk/N7a5mcgSWbxmtrRpTPAMfaKjegZ8OsowAYBMAsjugggDdrEa2pjgNEyjHQm83dAdXV1RSKVThcBcwVAhAdbWlrgdrvR2dnJtaqqhaxFqa6F1pPHxsYm+5UBlFAe0NzczJNdLhf0ej3XmkZZi8N68vj58xf7FQCbm0SM8mBDQwNPbmpqwuTkJNeaptVaT9npdJb15LG+vp4H0IGz6I90TE9Pw+3182BtbS1PplxfX1+otayFz+dDW1sb65SpJ508AuEY/EoIP36II3N2brGjvf2W2O0ED1ZVVfEiyqU1ZS2ob2xs5N23trZypp508lAURZzJofyZPOv06Oh+x+NxHqxEFP9V5PAHN6zyZbcF+NAAAAAASUVORK5CYII="
        return System.Drawing.Bitmap(System.IO.MemoryStream(System.Convert.FromBase64String(o)))

    def Flip(self, line, CX):
        if CX == True:
            if (line.Direction)[0] < 0:
                line.Flip()
        elif CX == False:
            if (line.Direction)[0] > 0:
                line.Flip()
        return line

    def Z_direction(self, Lines, Dir):
        ptZ = [cur.PointAt(0.5).Z for cur in Lines]
        max_z = ptZ.index(max(ptZ))
        min_z = ptZ.index(min(ptZ))
        Line1 = self.Flip(Lines[max_z], Dir)
        Line2 = self.Flip(Lines[min_z], Dir)
        return Line1, Line2

    def RunScript(self, Lines, Direc):
        if Lines:
            Topline, Endline = self.Z_direction(Lines, Direc)
            # return outputs if you have them; here I try it for you:
            return Topline, Endline





import GhPython
import System

class AssemblyInfo(GhPython.Assemblies.PythonAssemblyInfo):
    def get_AssemblyName(self):
        return "Line"

    def get_AssemblyDescription(self):
        return """子夜的Line类插件"""

    def get_AssemblyVersion(self):
        return "0.0.1"

    def get_AuthorName(self):
        return "CN-子夜"

    def get_Id(self):
        return System.Guid("3b533a10-f4b0-47f4-aa8e-2c8485bce9bd")