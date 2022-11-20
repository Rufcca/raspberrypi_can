from multiprocessing import Process,Pipe,Array
from can_module import *
from board_module import Board
from dash_module import *

def main():
    can_module = CanModule('socketcan','can0')
    can,board = Pipe()
    board_module = Board(board)

    board_array = Array('f',len(board_module.tags))
    
    can_p   = Process(target = can_module.raw_sender, args = (can,))
    board_p = Process(target = board_module.write_board, args = (board_array,))
    print_p = Process(target = dash_main, args = (board_array,))
    
    can_p.start()
    board_p.start()
    print_p.start()
    print_p.join()
    board_p.kill()
    can_p.kill()
    print('Final')

if __name__ == '__main__':
    main()
