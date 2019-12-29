all: guessmaker
guessmaker: guessing/guessmaker.cpp guessing/cpp-argparse/OptionParser.cpp
	g++ -std=c++0x -O3 $^ -o $@ -no-pie
