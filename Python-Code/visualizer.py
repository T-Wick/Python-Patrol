import matplotlib.pyplot as plt
import constants as c
from car import Car
from intersection import Intersection as Node
from road import Road
import numpy as np
import utility as util
import navigate as nv

car_data = None
nodes = None
edges = None
test_start = None
test_end = None

def drawMap(nodes,edges,text=False):
    if type(nodes) is dict:
        for key, node in nodes.items():
            plt.plot(node.x,node.y,linestyle='none',\
                marker=c.NODE_PLOT_SHAPE,markersize=c.NODE_PLOT_SIZE)
        for key, edge in edges.items():
            if type(edge.u) is int:
                u = nodes[str(edge.u)]
                v = nodes[str(edge.v)]
                plt.plot([u.x,v.x],[u.y,v.y],linestyle='-',\
                    color=c.EDGE_COLOR,linewidth=edge.num_lanes*c.PLOT_EDGE_WIDTH)
            else:
                #plt.plot([edge.u.x,edge.v.x],[edge.u.y,edge.v.y],linestyle='-',\
                #    color=c.EDGE_COLOR,linewidth=edge.num_lanes*c.PLOT_EDGE_WIDTH)
                plt.arrow(edge.u.x,edge.u.y,edge.v.x-edge.u.x,edge.v.y-edge.u.y,\
                    color=c.EDGE_COLOR,width=0.00001*edge.num_lanes,head_width=0.0001,length_includes_head=True)
                if text:
                    plt.text((edge.u.x+edge.v.x)/2,(edge.v.y+edge.u.y)/2,edge.id)
    else:
        nl = np.array([i.id for i in nodes])
        for inode in nodes:
            #draw node
            plt.plot(inode.x,inode.y,linestyle='none',\
                    marker=c.NODE_PLOT_SHAPE,markersize=c.NODE_PLOT_SIZE)
        for iedge in edges:
            #draw edges
            if type(iedge.u) == int:
                i = nodes[np.where(nl==str(iedge.u))[0][0]]
                j = nodes[np.where(nl==str(iedge.v))[0][0]]
                #print('plot',iedge.id,i.id,i.x,i.y,j.id,j.x,j.y)
                plt.plot([i.x,j.x],[i.y,j.y],linestyle='-',\
                    color=c.EDGE_COLOR,linewidth=edge.num_lanes*c.PLOT_EDGE_WIDTH)
            else:
                plt.plot([iedge.u.x,iedge.v.x],[iedge.u.y,iedge.v.y],\
                    linestyle='-',color=c.EDGE_COLOR,linewidth=edge.num_lanes*c.PLOT_EDGE_WIDTH)
                
                    
def drawPoint(pt1):
    plt.plot(pt1[0],pt1[1],linestyle='none',marker='o',markersize=12,color='red')


def drawCars(cars,draw=True):
    global car_data
    car_list = np.zeros((len(cars),2))
    it = 0
    for icar in cars:
        cur_p = icar.current_position
        if type(cur_p) is Node:
            car_list[it,0] = cur_p.x
            car_list[it,1] = cur_p.y
            #print(cur_p.id,cur_p.x,cur_p.y)
        else:
            #- car is on edge
            #car.ts_on_current_position
            portion = icar.ts_on_current_position / icar.current_position.time_steps #cur_steps
            
            if type(cur_p.u) is Node:
                car_list[it,0] = cur_p.u.x + (cur_p.v.x - cur_p.u.x) * portion
                car_list[it,1] = cur_p.u.y + (cur_p.v.y - cur_p.u.y) * portion
            else:
                print('plotting using id')
                car_list[it,0] = nodes[str(cur_p.u)].x + (nodes[str(cur_p.v)].x-nodes[str(cur_p.u)].x) * portion
                car_list[it,1] = nodes[str(cur_p.u)].y + (nodes[str(cur_p.v)].y-nodes[str(cur_p.u)].y) * portion

            
        it += 1
    if draw:
        car_data, = plt.plot(car_list[:,0],car_list[:,1],linestyle='none',\
            marker=c.CAR_PLOT_SHAPE,markersize=c.CAR_PLOT_SIZE,color='red')
    else:
        return car_list

def update(cars):
    global car_data
    car_list = drawCars(cars,draw=False)

    car_data.set_xdata(car_list[:,0])
    car_data.set_ydata(car_list[:,1])
    #- assum plt.draw() update only cars
    plt.draw()
    plt.pause(c.ANIMATION_SEG)
    

def init_graph(nodes,edges,cars,text=False):
    drawMap(nodes,edges,text=text)
    drawCars(cars)

if __name__ == '__main__':
    '''Note
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    !For now, ts on each road is set to be 10!
    !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    '''
    
    #- CONSTANTS are in constants.py Feel free to change
    
    nodes_file_path = 'map/nodes.npy'
    edges_file_path = 'map/edges.npy'
        
    nodes, edges = util.retreiveMap(place=(47.608013, -122.335167),distance=400,savefile=True)
    #nodes, edges = util.retreiveMap(place=(37.7749, -122.4194),distance=1000,savefile=True)

    #- If files do not exist, un-comment the line above and comment 3 lines below
    
    #nodes, edges = util.retreiveMap(fromfile=True,filename=(nodes_file_path,edges_file_path))
    
    #- nodes and edges in dictionary form
    nodes = util.node_to_object(nodes)
    edges = util.edge_to_object(edges)
    
    #add edges to nodes
    for key, edge in edges.items():
        edge.u = nodes[str(edge.u)]
        edge.v = nodes[str(edge.v)]
        nodes[str(edge.u)].add_edge(edge)
        nodes[str(edge.u)].cap += edge.num_lanes
        #nodes[str(edge.v)].add_edge(edge)
        nodes[str(edge.v)].cap += edge.num_lanes
    #- get seperate list of ids
    node_key = list(nodes.keys())
    edge_key = list(edges.keys())
    
    #test_end = (nodes[node_key[339]].x,nodes[node_key[339]].y)
    
    #- initialize navigator
    nv.init(nodes,edges,node_key,edge_key)
    
    #-some pairs of start and end dont work, do not why
    

    
    car_size = c.NUMBER_CARS
    
    #- pick random starts and ends
    cars_u = np.random.randint(len(nodes),size=car_size)
    cars_v = np.random.randint(len(nodes),size=car_size)
    cars =[]
    for i in range(car_size):
        st = nodes[node_key[cars_u[i]]]
        while st.isFull():
            n = np.random.randint(len(nodes))
            while n == cars_v[i]:
                n = np.random.randint(len(nodes))
            st = nodes[node_key[n]]
        cars.append(Car(st,nodes[node_key[cars_v[i]]]))
        st.add()
    
    #- have map and cars ready on plot
    init_graph(nodes,edges,cars)
    
    #- calculate shortest path for each car
    for car in cars:
        paths = nv.dk(car.start.id,car.dest.id)
        '''
        test_start = [car.start.x,car.start.y]
        test_end = [car.dest.x,car.dest.y]
        plt.plot(test_end[0],test_end[1],color='red',linestyle='none',marker='o',markersize=10)
        plt.plot(test_start[0],test_start[1],color='red',linestyle='none',marker='o',markersize=10)
        '''
        #paths = car.start.shortest_path(car.dest)
        while type(paths) is bool:
            print('Re-routing')
            #- when pair of starts and destinations do not work, get new destination
            r_v = np.random.randint(len(nodes),size=2)
            while r_v[0] == r_v[1]:
                r_v = np.random.randint(len(nodes),size=2)
            car.start=nodes[node_key[r_v[0]]]
            car.dest = nodes[node_key[r_v[1]]]
            paths = nv.dk(car.start.id,car.dest.id)
        #- add paths to car object
        #path_id = [p.id for p in paths]
        #paths = nv._expand_path(path_id)
        if len(paths) == 1:
            print('length is 1')
        car.set_path(paths[1:])
        for i in paths:
            print(str(i))
    
    '''
    cars = []
    car = Car(nodes['1178349180'],nodes['53160861'])
    nodes['1178349180'].add()
    cars.append(car)
    car.set_path(nv.dk(car.start.id,car.dest.id)[1:])
    _init_graph(nodes,edges,cars)
    '''


    counter=0
    while len(cars) > 0:
        for car in cars:
            if car.current_position.id == car.dest.id:
                counter+=1
                nodes[car.current_position.id].remove()
                cars.remove(car)
            else:
                nxt_move = str(car.paths[0].id)
                cur_pos = str(car.current_position.id)
                #print('car position', cur_pos, type(car.current_position))
                if type(car.current_position) == Road:
                    if car.ts_on_current_position < edges[cur_pos].time_steps:
                        car.ts_on_current_position += 1
                        continue
                else:
                    if car.ts_on_current_position < nodes[cur_pos].time_steps:
                        car.ts_on_current_position += 1
                        continue
                if nxt_move in edges:
                    if not edges[nxt_move].add():
                        print('on hold edge',edges[nxt_move])
                        continue
                    car.current_position = edges[nxt_move]
                    nodes[cur_pos].remove()
                    car.ts_on_current_position = 0
                elif nxt_move in nodes:
                    if not nodes[nxt_move].add():
                        print('on hold node',nodes[nxt_move])
                        continue
                    car.current_position = nodes[nxt_move]
                    edges[cur_pos].remove()
                    car.ts_on_current_position = 0
                car.paths.pop(0)
        update(cars)
    
    plt.ion()
    plt.show()
