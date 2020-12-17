import numpy as np
import g2o
import os
import pickle

def get_data(filename):
    load_file = open(filename,'rb')
    data = pickle.load(load_file)
    #print(data)
    return data

class PoseGraphOptimization(g2o.SparseOptimizer):
    def __init__(self):
        super().__init__()
        solver = g2o.BlockSolverSE3(g2o.LinearSolverCholmodSE3())
        solver = g2o.OptimizationAlgorithmLevenberg(solver)
        super().set_algorithm(solver)

    def optimize(self, max_iterations=20):
        super().initialize_optimization()
        super().optimize(max_iterations)

    def add_vertex(self, id, pose, fixed=False):
        v_se3 = g2o.VertexSE3()
        v_se3.set_id(id)
        v_se3.set_estimate(pose)
        v_se3.set_fixed(fixed)
        super().add_vertex(v_se3)

    def add_edge(self, vertices, measurement,
            information=np.identity(6),
            robust_kernel=None):

        edge = g2o.EdgeSE3()
        for i, v in enumerate(vertices):
            if isinstance(v, int):
                v = self.vertex(v)
            edge.set_vertex(i, v)

        edge.set_measurement(measurement)  # relative pose
        edge.set_information(information)
        if robust_kernel is not None:
            edge.set_robust_kernel(robust_kernel)
        super().add_edge(edge)

    def get_pose(self, id):
        return self.vertex(id).estimate()

    def make_vertices(self, data):
        lidar = data['scans']
        odom = data['odom']
        i = 0
        for scan in lidar:
            for point in scan:
                i = i+1
                q = g2o.Quaternion(0,0,0,0)
                t = g2o.Isometry3d(q,[point[0][0], point[0][1], point[0][2]])
                self.add_vertex(i, t)
        for f, point in enumerate(odom):
            if f % 2 == 0:
                i = i+1
                q = g2o.Quaternion(0,0,0,0)
                t = g2o.Isometry3d(q,[point[0][0], point[0][1], point[0][2]])
                self.add_vertex(i, t)
        print('num vertices:', len(super().vertices()))


if __name__ == '__main__':
    data = get_data('data3')
    opt = PoseGraphOptimization()
    opt.make_vertices(data)
