from cgi import test
import classes as cls
import matplotlib.pyplot as plt
import IO 


if __name__ == "__main__":
    # fig = plt.figure()
    test_class = True
    if test_class:
        #testing plates seems ok 24/5/2022
        test1 = cls.plate((0,0),(10,0),15,"AH32")
        print(test1.Ixx_c,test1.Iyy_c)
        print(test1.angle*180/3.14159,test1.length)
        print(test1.CoA)
        print(test1.calc_I_global({'axis': 'x','offset': 10}))
        rend = test1.render()[:2]
        # plt.plot(rend[0],rend[1])
        print("######## TEST1 ##############")

        #testing stiffener
        print("\n######## TEST2 ##############")
        test2 = cls.stiffener("fb",{'lw':10,'bw':1},0,"A",(0,0))
        print(test2.CoA)
        print(test2.area)
        print(test2.Ixx_c)
        print(test2.Iyy_c)
        # test2.render()
        [print(i.end) for i in test2.plates]
        
        #testing stiffener
        print("\n######## TEST3 ##############")
        test3 = cls.stiffener("g",{'lw':.525,'bw':1,'lf':.25,'bf':1},0,"A",(5,0))
        print(test3.CoA)
        print(test3.area)
        print(test3.Ixx_c)
        print(test3.Iyy_c)
        test3.render()
        [print(i.end) for i in test3.plates]
        
        print("\n######## TEST4 ##############")
        test4 = cls.stiff_plate(test1,1000,{'type':"g",'dims':{'lw':.525,'bw':1,'lf':.25,'bf':1},'mat':"A"})
        test4.render()
        # print(test4.stiffeners)
        print(IO.stiff_pl_save(test4))
        
        plt.show()
    else:
        data = IO.file_load("test.json")
        print(type(data))
        print(data['LBP'])
        print(type(data['geometry']))
        print(type(data['geometry'][0]))
