import numpy as np
import random
from contextlib import contextmanager

class clifford_simulator:
    """
    clifford gate인 H, CNOT, S gate와 Pauli 연산만을 통해서 양자 회로를 구성하면 고전적인 컴퓨터를 사용해도 효율적인 (polynomial한) simulation이 가능하다.
    이는 양자 상태를 직접 계산하는 것이 아니라 그 양자 상태에 대응되는 stabilizer group을 찾고 각 gate들에 의해서 stabilizer가 어떻게 변화하는지를 추적하였기 때문에 가능하다. 
    """
    # qubit수에 맞게 stabilizer를 기록할 변수들을 만든다.
    # tableau는 상태에 대한 stabilizer와 destabilizer를 각 qubit의 위치에 따른 X, Z Pauli를 통해서 표현한다. (Y는 X와 Z에 모두 1이 입력된 것으로 표현) (0~n-1: X, n~2n-1: Z)
    # r은 대응되는 stabilizer operator의 계수가 +1인지 -1인지를 기록한다. (0: +1, 1:-1)

    def __init__(self, num_qubit) -> None:
        # 사용하는 qubit의 수
        self.n = num_qubit
        # X와 Z를 기록하기 때문에 열이 2배가 되고 stabilizer와 destabilizer가 있기 때문에 행이 2배가 된다. 
        self.tableau = np.eye(2*num_qubit, 2*num_qubit, dtype=int)
        # stabilizer와 destabilizer의 계수를 기록할 array
        self.r = np.zeros(2*num_qubit, dtype=int)
        # 측정된 값을 기록할 array, 측정이 이루어지지 않으면 None으로 표현한다.
        self.measured_outcome = np.full(num_qubit, np.nan, dtype=object)
        self.deterministic_check = np.full(num_qubit, np.nan, dtype=object)

    # H gate와 S gate에서 phase 정보를 update하는 함수
    def r_update(self, qubit_index):

        x = self.tableau[:,qubit_index]
        z = self.tableau[:,qubit_index+self.n]
        #gate가 가해지는 qubit에 Pauli Y가 있는 stabilizer에 대해서 phase를 바꿈
        self.r ^= x*z

    # X gate는 그 qubit의 Pauli Z, Y의 phase를 바꾸게 된다. 
    def x(self, qubit_index):
        self.r ^= self.tableau[:,qubit_index + self.n]

    # Y gate는 그 qubit의 Pauli Z, X의 phase를 바꾸게 된다. 
    def y(self, qubit_index):
        self.r ^= self.tableau[:,qubit_index]
        self.r ^= self.tableau[:,qubit_index + self.n]

    # Z gate는 그 qubit의 Pauli X, Y의 phase를 바꾸게 된다. 
    def z(self, qubit_index):
        self.r ^= self.tableau[:,qubit_index]

    # H gate는 그 qubit의 Pauli X와 Pauli Z를 교환시킨다. Y의 경우 phase만 변화한다.
    def h(self, qubit_index):
        temp_row = np.copy(self.tableau[:, qubit_index])
        self.tableau[:,qubit_index] = self.tableau[:,qubit_index+self.n]
        self.tableau[:,qubit_index+self.n] = temp_row
        self.r_update(qubit_index)

    # X->Y, Y->-X, Z->Z
    def s(self, qubit_index):
        self.r_update(qubit_index)
        self.tableau[:,qubit_index+self.n] ^= self.tableau[:,qubit_index]

    # control qubit의 stabilizer와 target qubit의 stabilizer의 parity를 확인하여 target qubit의 상태를 결정한다.
    def cx(self, c, t):

        x_c = self.tableau[:,c]
        z_c = self.tableau[:,c+self.n]
        
        x_t = self.tableau[:,t]
        z_t = self.tableau[:,t+self.n]

        self.tableau[:,t] = x_t^x_c
        self.tableau[:,c+self.n] = z_t^z_c
        self.r ^= x_c*z_t*(x_t^z_c^1)

    # cz gate는 cx gate에 H gate를 사용하는 것으로 표현
    def cz(self, c,t):
        self.h(t)
        self.cx(c,t)
        self.h(t)

    # 계산에 사용되는 함수, Pauli 행렬로 표현된 x_1z_1, x_2z_2의 행렬 곱의 계수를 i의 거듭제곱으로 표현할 경우 그 지수.
    def g_function(self, x_1, z_1, x_2, z_2):
        if x_1 == 0 and z_1 == 0:
            return 0
        elif x_1 == 1 and z_1 == 1:
            return z_2 - x_2
        elif x_1 == 1 and z_1 == 0:
            return z_2*(2*x_2-1)
        elif x_1 == 0 and z_1 == 1:
            return x_2*(1-2*z_2)
        else:
            print(x_1, z_1)

    # 측정을 만들기 위해서 사용하는 연산
    def row_sum(self, h, i):
        checker = self.r[h]*2 +self.r[i]*2
        for j in range(self.n):
            checker += self.g_function(self.tableau[i,j], self.tableau[i, j+self.n], self.tableau[h,j], self.tableau[h, j+self.n])
        checker = checker % 4
        if checker == 0:
            self.r[h] = 0
        elif checker == 2:
            self.r[h] =1
        self.tableau[h, :] ^= self.tableau[i, :]
    # deterministic measure를 위해서 추가적인 row를 붙였다가 없애주는 계산
    @contextmanager
    def merging_and_explit(self):

        self.scratch = np.zeros(2*self.n, dtype=int)
        self.tableau = np.vstack((self.tableau, self.scratch))
        self.r = np.hstack((self.r, [0]))
        yield 
        self.scratch = self.tableau[-1]
        self.tableau = np.delete(self.tableau, -1, axis=0)
        self.r = np.delete(self.r, -1, axis = 0)

    # deteministic인지 아닌지에 따라서 다른 측정 방식을 사용    
    def measure(self, qubit_index, classical_bit):
        detrministic_ckeck = np.where(self.tableau[self.n:,qubit_index] == 1)[0]
        if len(detrministic_ckeck) > 0:
            self.random_measure(qubit_index, detrministic_ckeck[0]+self.n)
            self.deterministic_check[qubit_index] = False
        else:
            self.det_measure(qubit_index)
            self.deterministic_check[qubit_index] = True
    
    # non deterministic한 measure의 경우 Pauli X나 Y를 stabilizer에 포함하게 된다.
    # 이 경우 0이나 1로 상태가 50% 확률로 붕괴하게 된다. 
    def random_measure(self, qubit_index, p_row):
        with self.merging_and_explit() as f:
            i_list = list(range(2*self.n))
            # i!= p인 경우에 대해서만 실행
            i_list.remove(p_row)
            for i in i_list:
                # x_ia = 1인 경우만 실행
                if self.tableau[i,qubit_index] == 1:
                    self.row_sum(i, p_row)
            self.tableau[p_row-self.n, :] = self.tableau[p_row, :]
            self.r[p_row-self.n] = self.r[p_row]
            self.tableau[p_row, :] = np.zeros_like(self.tableau[p_row, :])
            self.tableau[p_row, self.n + qubit_index] = 1
            self.r[p_row] = random.randint(0,1)
            self.measured_outcome[qubit_index] = self.r[p_row]

    # deterministic한 경우에 대해서는 상태가 변화하지 않고 측정값만을 얻는다.
    def det_measure(self, qubit_index):
        with self.merging_and_explit() as f:
            for i in range(self.n):
                if self.tableau[i,qubit_index] == 1:
                    self.row_sum(2*self.n, i+self.n)

            self.measured_outcome[qubit_index] = self.r[-1]

    def get_sampling_result(self):
        for i, outcome in enumerate(self.measured_outcome):
            if np.isnan(outcome):
                self.measure(i,i)
        return str(self.measured_outcome)

if __name__ == '__main__':

    circ = clifford_simulator(3)
    circ.h(1)
    circ.h(2)
    circ.cz(0,1)
    circ.cz(1,2)
    circ.h(0)
    circ.measure(0,0)
    circ.cx(0,1)
    circ.s(1)
    circ.cx(0,1)
    circ.h(1)
    circ.measure(1,1)
    circ.h(2)
    circ.cz(1,2)
    circ.h(2)
    circ.cz(0,2)
    
    print(circ.tableau)
    print(circ.r)
    print(circ.measured_outcome)
    print(circ.deterministic_check)
    print(circ.get_sampling_result())

