import os
import json
from shutil import copytree, rmtree
from pbxproj import XcodeProject
from pbxproj.XcodeProject import FileOptions

ios_folder_name = "WAStickersThirdParty"
ios_root_folder = f"./iOS/{ios_folder_name}"

android_folder_name = "app/src/main"
android_root_folder = f"./Android/{android_folder_name}"


def update_ios_project():
    def move_files_to_folder():
        for file in ui_group_files:
            base_path = f"./WAStickersThirdParty"

            if os.path.exists(f"{base_path}/{file.path}") and not file.path.startswith("UI/"):
                os.rename(f"{base_path}/{file.path}",
                          f"{base_path}/UI/{file.path}")

        project.remove_group_by_id(ui_group.get_id())
        print(ui_group_files)

    def update_references():
        ui_group = project.get_or_create_group("UI", parent=root_group)
        base_path = f"./WAStickersThirdParty"

        for file in ui_group_files:
            if not file.path.startswith("UI/"):
                project.add_file(
                    f"{base_path}/UI/{file.path}", parent=ui_group)
            else:
                project.add_file(f"{base_path}/{file.path}", parent=ui_group)

    project = XcodeProject.load(f"{ios_root_folder}.xcodeproj/project.pbxproj")

    root_group = project.get_or_create_group(ios_folder_name)

    ui_group = project.get_or_create_group("UI", parent=root_group)
    ui_group_files = [project.get_file_by_id(
        file_id) for file_id in ui_group.children]

    move_files_to_folder()
    update_references()

    project.save()


stickerpacks = []


def clean_assets():
    if os.path.exists(f"{ios_root_folder}/Stickers/"):
        rmtree(f"{ios_root_folder}/Stickers/")

    if os.path.exists(f"{android_root_folder}/assets/"):
        rmtree(f"{android_root_folder}/assets/")


def copy_assets():
    for stickerpack in os.listdir("./Stickers"):
        stickers = []
        tray_image = ""

        if stickerpack != ".DS_Store":
            copytree(f"./Stickers/{stickerpack}",
                     f"{ios_root_folder}/Stickers/{stickerpack}")
            copytree(f"./Stickers/{stickerpack}",
                     f"{android_root_folder}/assets/{stickerpack}")

            for sticker in os.listdir(f"./Stickers/{stickerpack}"):
                if sticker != ".DS_Store" and not sticker.startswith("tray_"):
                    stickers.append(sticker)
                elif sticker.startswith("tray_"):
                    tray_image = sticker

            stickerpacks.append(
                {stickerpack: {"stickers": stickers, "tray": tray_image}})


def make_stickerpack_json():
    json_file = {"android_play_store_link": "",
                 "ios_app_store_link": "", "sticker_packs": []}

    for _stickerpack in stickerpacks:
        stickerpack_name = list(_stickerpack.keys())[0]
        stickerpack = _stickerpack[stickerpack_name]

        stickerpack_list = {"identifier": stickerpack_name, "name": f"{stickerpack_name} Sticker Pack", "publisher": "Avinoam",
                            "tray_image_file": stickerpack["tray"], "publisher_email": "", "publisher_website": "", "privacy_policy_website": "", "license_agreement_website": ""}
        stickerpack_list["stickers"] = [
            {"image_file": sticker} for sticker in stickerpack["stickers"]]

        json_file["sticker_packs"].append(stickerpack_list)

    with open(f"{ios_root_folder}/sticker_packs.wasticker", "w") as file:
        file.write(json.dumps(json_file))

    with open(f"{android_root_folder}/assets/contents.json", "w") as file:
        file.write(json.dumps(json_file))


def add_stickers_to_xcode():
    project = XcodeProject.load(f"{ios_root_folder}.xcodeproj/project.pbxproj")

    root_group = project.get_or_create_group(ios_folder_name)
    project.add_folder(f"{ios_root_folder}/Stickers", parent=root_group, file_options=FileOptions(ignore_unknown_type=True))

    project.save()


# update_ios_project()
clean_assets()
copy_assets()
make_stickerpack_json()
add_stickers_to_xcode()
