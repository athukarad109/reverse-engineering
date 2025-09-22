
%.s : %.c
	gcc -fPIC -std=c99 -g -S -O0 -o $@ $^

%.o : %.c
	gcc -fPIC -std=c99 -g -c -O0 -o $@ $^

%.odump : %.o
	objdump -htsdr -Mintel $^ > $@

%.so : %.o
	gcc -shared -o $@ $^

%.sodump : %.so
	objdump -htsdr -Mintel $^ > $@

smallLib.so : struct.o array.o linkedlist.o tree.o if.o ifelse.o switch.o while.o for.o
	gcc -shared -o $@ $^

primitive_exe.o : primitive.c
	gcc -std=c99 -g -c -O0 -o $@ $^

primitive : primitive_exe.o
	gcc -o $@ $^

primitive.edump : primitive
	objdump -htsd -Mintel $^ > $@

clean:
	-rm *.s
	-rm *.o
	-rm *.odump
	-rm *.so
	-rm *.sodump
	-rm primitive
	-rm *.edump
