# importing the module
import cv2
import numpy as np
points = []

# function to display the coordinates of
# of the points clicked on the image
def click_event(event, x, y, flags, params):
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print((y, x))
        points.append([y, x])
        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, str(x) + ',' +
                    str(y), (x, y), font,
                    0.5, (255, 0, 0), 1)
        cv2.imshow('image', img)

    # checking for right mouse clicks    
    if event == cv2.EVENT_RBUTTONDOWN:
        # displaying the coordinates
        # on the Shell
        print(x, ' ', y)

        # displaying the coordinates
        # on the image window
        font = cv2.FONT_HERSHEY_SIMPLEX
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]
        cv2.putText(img, str(b) + ',' +
                    str(g) + ',' + str(r),
                    (x, y), font, 1,
                    (255, 255, 0), 2)
        cv2.imshow('image', img)


# driver function
if __name__ == "__main__":
    # reading the image
    import json
    from map_grid import preprocess
    """
    这是一个根据现有图像和图像配置文件，生成way_points属性的工具(自动按照顺序添加至json)
    配置好name, 鼠标左键点击地图，生成way_points
    """
    # 【配置我！！！】
    name = "de_dust2"
    # load config
    path = r".\dir\{}.png".format(name)
    conf_path = r".\dir\{}.json".format(name)
    with open(conf_path, "r") as f:
        conf = json.load(f)
        sz = (int(conf['scale_size'][0]), int(conf['scale_size'][1]))
        threshold = conf["threshold"]

    image = preprocess(path, sz, threshold)
    img = cv2.cvtColor(np.float32(image), cv2.COLOR_GRAY2RGB)
    # displaying the image
    cv2.imshow('image', img)
    # setting mouse handler for the image
    # and calling the click_event() function
    cv2.setMouseCallback('image', click_event)

    # wait for a key to be pressed to exit
    cv2.waitKey(0)

    # close the window
    cv2.destroyAllWindows()
    with open(conf_path, "w") as f:
        conf["way_points"] = points
        json.dump(conf, f)