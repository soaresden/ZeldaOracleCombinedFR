import sys
from pyboy import PyBoy
rom,out=sys.argv[1:3]
pb=PyBoy(rom,window='null',cgb=True,sound_emulated=True,sound_volume=0)
pb.set_emulation_speed(0)
pb.tick(1500,False); pb.button('start',4); pb.tick(300,False)
for i in range(6):
    for a in (0xc485,0xc48b): pb.memory[a] &= 0xfd
    pb.tick(1,True)
pb.screen.image.convert('RGB').save(out+'_bg.png')
for i in range(6): pb.tick(1,True)
pb.stop(save=False)
