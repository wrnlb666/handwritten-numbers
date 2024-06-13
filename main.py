import math
from typing import (
    Tuple
)

import pyray as ray

import numpy as np
import keras
import tensorflow as tf


def load_model():
    return keras.saving.load_model("number.keras")


def board_pos2pixel(x: int, y: int) -> Tuple[int, int]:
    posx: int = x * 15 + 90
    posy: int = y * 15 + 90
    return posx, posy

def board_pixel2pos(x: int, y: int) -> Tuple[int, int]:
    posx: int = (x - 90) // 15
    posy: int = (y - 90) // 15
    return posx, posy


def board_init() -> list[list[float]]:
    return [[0 for _ in range(28)] for _ in range(28)]


def board_clear(board: list[list[float]]) -> None:
    for i in range(28):
        for j in range(28):
            board[i][j] = 0


def main() -> None:
    # keras initialize
    model = load_model()

    # raylib initialize
    ray.init_window(800, 600, "number")
    ray.set_target_fps(60)
    raywhite: ray.Color = ray.Color(
        ray.RAYWHITE[0], 
        ray.RAYWHITE[1], 
        ray.RAYWHITE[2], 
        ray.RAYWHITE[3],
    )
    black: ray.Color = ray.Color(
        ray.BLACK[0],
        ray.BLACK[1],
        ray.BLACK[2],
        ray.BLACK[3],
    )
    orange: ray.Color = ray.Color(
        ray.ORANGE[0],
        ray.ORANGE[1],
        ray.ORANGE[2],
        ray.ORANGE[3],
    )


    # status
    status_drawing: int = 0
    status_result: int = 1
    status: int = status_drawing

    # game data
    board: list[list[float]] = board_init()

    # status_drawing status
    reset_button_rec: ray.Rectangle = ray.Rectangle(550, 180, 210, 40)
    guess_button_rec: ray.Rectangle = ray.Rectangle(550, 380, 210, 40)
    board_rec: ray.Rectangle = ray.Rectangle(90, 90, 510, 510)
    mouse_down: bool = False

    # status result data
    arr = np.array(board).reshape(28, 28, 1)
    guess_res = None
    return_button_rec: ray.Rectangle = ray.Rectangle(300, 400, 200, 40)



    while not ray.window_should_close():
        if status == status_drawing:
            # handle board mouse input
            mouse_x: int = ray.get_mouse_x()
            mouse_y: int = ray.get_mouse_y()

            if ray.is_mouse_button_pressed(0):
                mouse_down = True
            if ray.is_mouse_button_released(0):
                mouse_down = False

            if ray.check_collision_point_rec(ray.Vector2(mouse_x, mouse_y), board_rec):
                if mouse_down:
                    # set gray scale of effected rectangles
                    (x, y) = board_pixel2pos(mouse_x, mouse_y)

                    for _ in range(1):
                        if x >= 0 and x < 28 and y >= 0 and y < 28:
                            board[x][y] = 1
                        else:
                            break
                        if x-2 >= 0:
                            board[x-2][y] = 0.3
                        if x-1 >= 0:
                            board[x-1][y] = 0.6
                        if x+1 < 28:
                            board[x+1][y] = 0.6
                        if x+2 < 28:
                            board[x+2][y] = 0.3
                        if y-2 >= 0:
                            board[x][y-2] = 0.3
                        if y-1 >= 0:
                            board[x][y-1] = 0.6
                        if y+1 < 28:
                            board[x][y+1] = 0.6
                        if y+2 < 28:
                            board[x][y+2] = 0.3
                        if x-1 >= 0 and y-1 >= 0:
                            board[x-1][y-1] = 0.5
                        if x+1 < 28 and y-1 >= 0:
                            board[x+1][y-1] = 0.5
                        if x-1 >= 0 and y+1 < 28:
                            board[x-1][y+1] = 0.5
                        if x+1 < 28 and y+1 < 28:
                            board[x+1][y+1] = 0.5



            # begin drawing
            ray.begin_drawing()
            # clear background
            ray.clear_background(raywhite)

            # draw 28 * 28 drawing board
            # fill color
            ray.draw_rectangle(90, 90, 420, 420, orange)

            # draw lines
            step: int = 15
            spos_x: int = 90
            epos_x: int = 90
            spos_y: int = 90
            epos_y: int = 510
            for _ in range(29):
                ray.draw_line(spos_x, spos_y, epos_x, epos_y, black)
                spos_x += step
                epos_x += step
            spos_x: int = 90
            epos_x: int = 510
            spos_y: int = 90
            epos_y: int = 90
            for _ in range(29):
                ray.draw_line(spos_x, spos_y, epos_x, epos_y, black)
                spos_y += step
                epos_y += step

            # fill color based on gray scale
            for i, v in enumerate(board):
                for j, v in enumerate(v):
                    if v != 0:
                        color: ray.Color = ray.color_from_hsv(200, v, 0.8)
                        (posx, posy) = board_pos2pixel(i, j)
                        ray.draw_rectangle(posx, posy, 15, 15, color)
                

            # draw button
            if ray.gui_button(reset_button_rec, "reset"):
                board_clear(board)
            if ray.gui_button(guess_button_rec, "guess"):
                status = status_result
                arr = np.zeros((28, 28))
                for i in range(28):
                    for j in range(28):
                        arr[i][j] = board[j][i]
                arr = arr.reshape((1, 28, 28, 1))
                # arr = np.expand_dims(arr, 0)
                # arr = np.expand_dims(arr, -1)
                # print(arr)
                guess_res = model.predict(arr)
                print(guess_res)

            ray.end_drawing()



        else:
            # handle board mouse input
            if ray.is_mouse_button_pressed(0):
                mouse_down = True
            if ray.is_mouse_button_released(0):
                mouse_down = False

            # drawing
            ray.begin_drawing()
            ray.clear_background(raywhite)

            temp: list[float] = guess_res[0].tolist()
            # print(res)
            res: list[list[int|float]] = [[i, v] for i, v in enumerate(temp)]
            res.sort(reverse=True, key=lambda l: l[1])

            ray.draw_text(f"num: {res[0][0]}, confidence: {float(res[0][1]*100):.3}%", 200, 200, 36, black)
            ray.draw_text(f"num: {res[1][0]}, confidence: {float(res[1][1]*100):.3}%", 200, 250, 36, black)
            ray.draw_text(f"num: {res[2][0]}, confidence: {float(res[2][1]*100):.3}%", 200, 300, 36, black)
            # print(map)
            # print(highest)
            
            if ray.gui_button(return_button_rec, "return"):
                board_clear(board)
                status = status_drawing


            ray.end_drawing()




    # TODO: do cleanup if needed
    ray.close_window()




def test() -> None:
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
    x_test = x_test.astype("float32") / 255
    x_test = np.expand_dims(x_test, -1)
    print(x_test.shape)

    num_classes = 10
    y_test = keras.utils.to_categorical(y_test, num_classes)

    model = load_model()

    score = model.evaluate(x_test, y_test, verbose=0)
    print("Test loss:", score[0])
    print("Test accuracy:", score[1])

    print(x_test[:1])
    print(y_test[:1])
    pass


if __name__ == "__main__":
    main()
