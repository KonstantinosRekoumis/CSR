import classes as cls
import render as rnr
import matplotlib.pyplot as plt
import physics as phzx
import IO 


if __name__ == "__main__":
    # fig = plt.figure()
    test_class = False
    if test_class:
        #testing plates seems ok 24/5/2022
        test1 = cls.plate((0,0),(10,0),15,"AH32","a",bilge=False)
        print(test1)
        print(test1.Ixx_c,test1.Iyy_c)
        print(test1.angle*180/3.14159,test1.length)
        print(test1.CoA)
        print(test1.calc_I_global({'axis': 'x','offset': 10}))
        test1.render(r_m='wC')
        plt.show()
        # plt.plot(rend[0],rend[1])
        print("######## TEST1 ##############")

        # #testing stiffener
        # print("\n######## TEST2 ##############")
        # test2 = cls.stiffener("fb",{'lw':10,'bw':1},0,"A",(0,0))
        # print(test2.CoA)
        # print(test2.area)
        # print(test2.Ixx_c)
        # print(test2.Iyy_c)
        # # test2.render()
        # [print(i.end) for i in test2.plates]#
        
        # #testing stiffener
        # print("\n######## TEST3 ##############")
        # test3 = cls.stiffener("g",{'lw':525,'bw':1,'lf':250,'bf':1},0,"A",(5,0))
        # print(test3.CoA)
        # print(test3.area)
        # print(test3.Ixx_c)
        # print(test3.Iyy_c)
        # test3.render()
        # [print(i.end) for i in test3.plates]
        
        # print("\n######## TEST4 ##############")
        # test4 = cls.stiff_plate(test1,1000,{'type':"g",'dimensions':{'lw':525,'bw':1,'lf':250,'bf':1},'material':"A"})
        # test4.render()
        # # print(test4.stiffeners)
        # print(IO.stiff_pl_save(test4))
        
        # plt.show()
    else:
        papor = IO.load_ship("test.json")
        print(papor.Ixx)
        # print(papor.stiff_plates)
        [print(i.coords) for i in papor.blocks]
        papor.render(r_m = 'wC')
        # # rnr.contour_plot(papor,show_w=True,key = 'thickness')
        # rnr.block_plot(papor,fill=True)
        # phzx.BSP_total_eval(papor,15.3)
        phzx.HSM_total_eval(papor,15.3)
        IO.ship_save(papor,"blyat1.json")
        