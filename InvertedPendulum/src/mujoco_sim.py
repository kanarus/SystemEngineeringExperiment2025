from dm_control import mujoco
import pathlib


def main():
    # model = mujoco.MjModel.from_xml_path(str(pathlib.Path(__file__).parent / 'simulator' / 'acrobot.xml'))
    # data = mujoco.MjData(model)
    # launch(model, data)

    physics = mujoco.Physics.from_xml_path(str(pathlib.Path(__file__).parent / 'simulator' / 'acrobot.xml'))
    


if __name__ == "__main__":
    main()
