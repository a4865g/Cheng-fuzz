#!/usr/bin/python3
import sys
import matplotlib.pyplot as plt
def main():
    
    if len(sys.argv) < 2:
        print("Usage: ./fuzz_graph.py [queue1_plot_data] [plot_data_label1] [queue2_plot_data] [plot_data_label2]... [title]")
    else:
        # for i in range(1, len(sys.argv)-1, 2):
        #     init_time = 0
        #     x = []
        #     y = []
        #     print(sys.argv[i])
        #     f = open(sys.argv[i], 'r')
        #     lines = f.readline()
        #     lines = f.readlines()
        #     f.close()
        #     x.append(0) # init
        #     y.append(0) # init
        #     for line in lines:
        #         time=int(line.split(',', 13)[0].strip()) / 60
        #         x.append(time)
        #         map_size = int(line.split(',', 13)[12].strip())
        #         y.append(map_size)
            
        #     plt.plot(x, y, label = sys.argv[i+1])

        x = []
        y = []
        print(sys.argv[1])
        f = open(sys.argv[1], 'r')
        lines = f.readline()
        lines = f.readlines()
        f.close()
        x.append(0) # init
        y.append(0) # init
        for line in lines:
            time=int(line.split(',', 13)[0].strip()) / (60 * 60)
            if(time > 24):
                break
            x.append(time)
            map_size = int(line.split(',', 13)[12].strip())
            y.append(map_size)
        
        plt.plot(x, y, label = sys.argv[1+1])

        x = []
        y = []
        print(sys.argv[3])
        f = open(sys.argv[3], 'r')
        lines = f.readline()
        lines = f.readlines()
        f.close()
        x.append(0) # init
        y.append(0) # init
        for line in lines:
            time=int(line.split(',', 13)[0].strip()) / (60 * 60)
            if(time > 24):
                break
            x.append(time)
            map_size = int(line.split(',', 13)[12].strip())
            y.append(map_size)
        
        plt.plot(x, y, label = sys.argv[1+3])

        # naming the x axis
        plt.xlabel('Time (HR)')
        # naming the y axis
        plt.ylabel('Edge Coverage')
        # giving a title to my graph
        plt.title(sys.argv[len(sys.argv)-1])

        
        # show a legend on the plot
        plt.legend()
        
        # function to show the plot
        plt.show()
if __name__ == "__main__":
    main()

