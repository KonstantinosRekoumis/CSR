import modules.classes as cls
import modules.render as rnr
import matplotlib.pyplot as plt
import modules.physics as phzx
import modules.rules as csr
import modules.IO as IO


if __name__ == "__main__":
    # fig = plt.figure()
    test_class = False
    if test_class:
        # #testing plates seems ok 24/5/2022
        test1 = cls.plate((-10,0),(10,5),15,"AH32",'Shell')
        # print(test1)
        # print(test1.Ixx_c,test1.Iyy_c)
        # print(test1.angle*180/3.14159,test1.length)
        # print(test1.CoA)
        # print(test1.calc_I_global({'axis': 'x','offset': 10}))
        # test1.render(r_m='wC')
        # plt.show()
        # # plt.plot(rend[0],rend[1])
        # print("######## TEST1 ##############")

        # #testing stiffener
        # print("\n######## TEST2 ##############")
        # test2 = cls.stiffener("fb",{'lw':10,'bw':1},0,"A",(0,0))
        # print(test2.CoA)
        # print(test2.area)
        # print(test2.Ixx_c)
        # print(test2.Iyy_c)
        # # test2.render()
        # [print(i.end) for i in test2.plates]#
        
        #testing stiffener
        print("\n######## TEST3 ##############")
        test3 = cls.stiffener("tb",{'lw':525,'bw':1,'lf':250,'bf':1},0,(5,0),"A",'Shell')
        for i in test3.plates:
            i.cor_thickness = 1e-3
        test3.update()
        print("CoA",test3.CoA)
        print("area",test3.area)
        print("Ixx_c",test3.Ixx_c)
        print("Iyy_c",test3.Iyy_c)
        print("n50_Ixx_c",test3.n50_Ixx_c)
        print("n50_Iyy_c",test3.n50_Iyy_c)
        # test3.render()
        [print(i) for i in test3.plates]
        
        print("\n######## TEST4 ##############")
        test4 = cls.stiff_plate(-1,test1,1000,0,0,{'type':"tb",'dimensions':{'lw':525,'bw':1,'lf':250,'bf':1},'material':"A"},0)
        print("CoA",test4.CoA)
        print("Ixx_c",test4.Ixx_c)
        print("Iyy_c",test4.Iyy_c)
        print("n50_Ixx_c",test4.n50_Ixx_c)
        print("n50_Iyy_c",test4.n50_Iyy_c)
        test4.plate.render()
        test4.render(r_m= 'wC')
        # print(test4.stiffeners)
        print(IO.stiff_pl_save(test4))
        
        plt.show()
    else:
        papor = IO.load_ship("test.json")
        # print(papor.Ixx)
        # # print(papor.stiff_plates)
        # [print(i.coords) for i in papor.blocks]
        papor.render(r_m = 'wC',path='section.pdf')
        HSM = phzx.Dynamic_total_eval(papor,15.3,'HSM',LOG=False)
        FLC =  {
        'Dynamics':'S+D',
        'max value': 'DC',
        'skip value':'LC,WB,OIL,FW,VOID'
        }
        [csr.Loading_cases_eval(papor,case,FLC) for case in HSM]
        out = cls.DataLogger()
        data = out.CreateTabularData(papor,['HSM-1','HSM-2'])
        for i in data:
            print('%'*40)
            for j in i:
                print(j)
            print('%'*40)
        # # rnr.contour_plot(papor,show_w=True,key = 'id')
        # rnr.block_plot(papor,fill=True)
        # rnr.pressure_plot(papor,'NORMALS','DC',normals_mode=True)
        # rnr.pressure_plot(papor,'NORMALS','WB',normals_mode=True)
        # phzx.BSP_total_eval(papor,15.3)
        # phzx.HSM_total_eval(papor,15.3)
        # phzx.Dynamic_total_eval(papor,15.3,'HSM',LOG=False)
        # for i in papor.blocks:
        #     if i.space_type == 'DC':
        #         print(i.coords)
        # rnr.pressure_plot(papor,'H
        # SM-1','all')
        # rnr.pressure_plot(papor,'HSM-2','DC')
        # rnr.pressure_plot(papor,'BSP-1P','DC')
        # rnr.pressure_plot(papor,'BSP-2P','DC')
        # papor.LaTeX_output(Debug=True)
        # IO.ship_save(papor,"blyat1.json")
# 
