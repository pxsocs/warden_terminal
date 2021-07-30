import emoji
from ansi.colour import fg


def logo():
    print(
        fg.brightgreen(f"""
  _   _           __        ___    ____     _
 | |_| |__   ___  \ \      / / \  |  _ \ __| | ___ _ __
 | __| '_ \ / _ \  \ \ /\ / / _ \ | |_) / _` |/ _ \ '_  |
 | |_| | | |  __/   \ V  V / ___ \|  _ < (_| |  __/ | | |
  \__|_| |_|\___|    \_/\_/_/   \_\_| \_\__,_|\___|_| |_|"""))
    print("")
    print(
        emoji.emojize(
            "                                          Node Edition :key:"))
    print(
        fg.boldyellow(
            "                             Powered by NgU technology "))


def goodbye():
    for n in range(0, 100):
        print("")
    print(
        fg.brightgreen(f"""
   \ \ / (_)_ _ ___ ___
    \ V /| | '_/ -_|_-<
     \_/ |_|_| \___/__/
           (_)_ _
    _  _   | | '  |         _
   | \| |_ |_|_||_| ___ _ _(_)___
   | .` | || | '  \/ -_) '_| (_-<
   |_|\_|\_,_|_|_|_\___|_| |_/__/
"""))

    print(fg.boldyellow("    If you enjoyed the app..."))
    print("")
    print(
        fg.brightgreen(
            "    tipping.me (Lightning): https://tippin.me/@alphaazeta"))
    print("")
    print(
        fg.brightgreen(
            "    onchain: bc1q4fmyksw40vktte9n6822e0aua04uhmlez34vw5gv72zlcmrkz46qlu7aem"
        ))

    # print("""
    # ▄▄▄▄▄▄▄     ▄▄  ▄  ▄  ▄▄▄▄▄▄▄
    # █ ▄▄▄ █ ▀ ▀▄▀ █▀ ▀█ ▀ █ ▄▄▄ █
    # █ ███ █ ▀█▀▄▄▀█ ▄▀ █▀ █ ███ █
    # █▄▄▄▄▄█ █▀▄ █▀█▀█▀█ ▄ █▄▄▄▄▄█
    # ▄▄▄▄▄ ▄▄▄█▀ ▄▄▄▀▄▄▄▀▄▄ ▄ ▄ ▄
    # █▀▄ █▄▄▀▄ █▀▄▀▄▄ ▄▄▀▄▄█▄█▄▄▀▀
    # █▀▄  █▄▄ ▄▄▄█▄█▄█▄▄▄▀  ▄▀▀▄▀
    # ▄▀▀▄▀ ▄   ▄▀▄▄█▄█▄ ▀▀ ▀████ ▀
    # █▄█▄██▄ ▄█▀▀▀▄█▀▀▄  ▄ ▀▄▀▀▄▄▄
    # █    ▄▄▀█ ▀▀  ▀▄▀ ▄▀▀▄▀▄▀▄▀▀▀
    # █ █ ▀▀▄▄█▀▀ ▀▄███▄ █▄█▄▄█▀▄█▀
    # ▄▄▄▄▄▄▄ █▀ ▀▄ █▄  ▄▄█ ▄ █▀█▀▀
    # █ ▄▄▄ █ ▄▀▄█▀▄▄▄█▄▀▀█▄▄▄█▄▄█▀
    # █ ███ █ █ ▄▀▄ ▄▄█▄▄█▀▄▄▄▄ █▄▀
    # █▄▄▄▄▄█ █    ▄▄▄█▄█▄▀▀█ ▄▀▄▀
    # """)

    print("")
    print(fg.boldyellow("    [i] Shutting down. Please wait..... "))
    print("")


def umbrel():
    return (fg.magenta("""
              ,;###GGGGGGGGGGl#Sp
           ,##GGGlW""^'  '`""%GGGG#S,
         ,#GGG"                  "lGG#o
        #GGl^                      '$GG#
      ,#GGb                          GGG,
      lGG"                            "GGG
     #GGGlGGGl##p,,p##lGGl##p,,p###ll##GGGG
    !GGGlW''''''*GGGGGGG#'WlGGGGG#W''*WGGGGS
     ''          '^          ''          ''

                @GGS         lG#
                !GGG        !GGG
                !GGG        !GGG
                !GGG        !GGG
                !GGG        !GGG
                !GGG        !GGG
                'GGG        $GGl
                 "GGG#psqp##GG#
                   "%GGGGGG# """))
