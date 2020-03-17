#pragma once
#include "opencv2/imgproc.hpp"
#include "opencv2/highgui.hpp"
#include "opencv2/videoio.hpp"
#include "opencv2/core/core.hpp"
using namespace cv;
using namespace std;


//int minold = 320; 				     // изначально предполгаем, что линия будет в центре кадра 
					   // далее в данную переменную будут записываться значение предыдучего центра линии
namespace line2 {

	void StartWithSvet2(Mat frame) {
		Mat gray;
		cvtColor(frame, gray, COLOR_BGR2HSV);
		inRange(gray, Scalar(45, 136, 137), Scalar(72, 255, 255), gray);
		blur(gray, gray, Size(3, 3));
		imshow("gray", gray);
		vector<Vec3f> detected_circles;
		HoughCircles( gray, detected_circles, CV_HOUGH_GRADIENT, 1, 20, 20, 20, 0, 30);

		for (size_t i=0; i < detected_circles.size(); ++i) {
			int x = cvRound(detected_circles[i][0]);
			int y = cvRound(detected_circles[i][1]);
			int r = cvRound(detected_circles[i][2]);
			cout << "found\n";
			circle(frame, Point(x, y), r, Scalar(0, 0, 255), 3);
		}

	}


	int distance(int x1, int y1, int x2, int y2) {
		return (x1 - x2)*(x1 - x2) + (y1 - y2)*(y1 - y2);
	}

	vector<Vec3f>detect3xCircle(Mat gray, Mat frame, bool debug=true) {
		vector<Vec3f> detected_circles;
		HoughCircles( gray, detected_circles, CV_HOUGH_GRADIENT, 1, 20, 40, 30, 10, 30);

		vector<Vec3f>tmp;
		for (size_t i=0; i < detected_circles.size(); ++i) {
			int x1 = cvRound(detected_circles[i][0]);
			int y1 = cvRound(detected_circles[i][1]);
			int r1 = cvRound(detected_circles[i][2]);

			circle(frame, Point(x1, y1), r1, Scalar(0, 0, 255), 3);
			tmp.emplace_back(detected_circles[i]);

			for (size_t j=0; j < detected_circles.size(); ++j) {
				int x2 = cvRound(detected_circles[j][0]);
				int y2 = cvRound(detected_circles[j][1]);
				int r2 = cvRound(detected_circles[j][2]);

				if (x1 == x2 && y1==y2 && r1 == r2)
					continue;

				circle(frame, Point(x2, y2), r2, Scalar(0, 0, 255), 3);

				if (distance(x1, y1, x2, y2) <= 12000) {
					tmp.emplace_back(detected_circles[j]);
				}
				if (tmp.size() == 3)
					break;
			}
			if (tmp.size() == 3)
				break;
		}
		if (debug)
			printf("Lenght 3x-circle: %ld \n", tmp.size());

	return tmp;
	}
	


	bool comp(Vec3f a, Vec3f b) {
		return a[1] > b[1];
	}

	void StartWithSvet(Mat img){
		Mat gray;
		cvtColor(img, gray, COLOR_BGR2GRAY);
		blur(gray, gray, Size(3, 3));

		vector<Vec3f>circles;
		circles = detect3xCircle(gray, img);

		if (circles.size() == 3) {
			sort(circles.begin(), circles.end(), comp);
			for (size_t i=0; i < circles.size(); ++i) {
				int x = cvRound(circles[i][0]);
				int y = cvRound(circles[i][1]);
				int r = cvRound(circles[i][2]);
				vector<Mat>BGR;
				split(img, BGR);
				Vec3b data = BGR[0].at<Vec3b>(x-1, y-1);

				int blue = data[0];//img[y-1][x-1][0];
				int green = data[1];//img[y-1][x-1][1];
				int red = data[2];//img[y-1][x-1][2];

				if (i == 0) {
					printf("red --> %d, %d, %d \n", red, green, blue);
					if (red >= 200 && green >= 20 && blue >= 20) {
						circle(img, Point(x, y), 1, Scalar(255, 0, 0), 2);
						printf("RED FOUND \n");
						break;
					}
				}
				else if (i == 1) {
					printf("yellow --> %d, %d, %d \n", red, green, blue);
					if (red >= 200 && green >= 200 && blue >= 10) {
						circle(img, Point(x, y), 1, Scalar(255, 0, 0), 2);
						printf("YELLOW FOUND \n");
						break;
					}
				}
				else {
					printf("green --> %d, %d, %d \n", red, green, blue);
					if (red >= 20 && green >= 190 && blue >= 0) {
						circle(img, Point(x, y), 1, Scalar(255, 0, 0), 2);
						printf("GREEN FOUND \n");
					}
				}
			}
		}


	}

	void MyFilledCircle(Mat img, Point center);

	int FindLine(Mat line, int minold,int View,bool debug = false)
	{

		int N = View;      // номер строки картинки, которую будем анализировать (почти низ картинки)

		int w = 0;        //номер белого пикселя после черной последовательности
		int centr = 0;    //центр черной линии

		int r = 0;        //для массива
		int mas[640];     //больше 640 центров не будет т.к. в принципе пикселей в строке 640


		for (int c = 150; c < line.cols-150; c++)
		{
			int b = c;    //для расчета ширины линии
			int e = b;

			while ((e < 640) && ((line.at<Vec3b>(N, e)[2]) < 50) && ((line.at<Vec3b>(N, e)[1]) < 50) && ((line.at<Vec3b>(N, e)[0]) < 50)) // если черный или темный
			{
				e++; //контролируем длину строки 
			}

			w = e; //номер первого белого пикселя после черной последовательности пикселей

			int lin = e - b; // от конца e отнимаю начало b таким образом определяю ширину черного объекта
			//if ((lin < 100) && (lin > 200)) // проверка линии. По пикселям линия будет иметь некоторый диапазон, если это не СТОП линия или перекресток

			if (lin < 50)
				continue;
			centr = (b + w) / 2; // расчет центра черного объекта

			c = e;               //присваиваем счетчику для for новое значение, чтобы он заного не начал перебирать пиксели откуда начал предыдущий раз 

			mas[r] = centr;      // записываем в массив центр черного объекта
			r++;                 // увеличиваем счетчик для массива, чтобы записать элементы по порядку
		}


		int min = 640;
		for (int i = 0; i < r; i++)         //поиск ближайшего элемента массива (центра черного объекта) к пикселю 320 (координата по Х)
		{
			if (abs(mas[i] - minold) < min) //ВМЕСТО 320 СТАВИМ ЗНАЧЕНИЕ ПРЕДЫДУЩЕГО КАДРА
											//Резкий уход линии в сторону не возможен из-за низкой скорости ТС и конфигурации поля 
											//поэтому ближайшая линия к предыдущему кадру и будет линии, по которой движется робот, 
											//а например не встречная
			{
				min = mas[i];
			}
		}
		if (debug) {
			MyFilledCircle(line, Point(min, N));// рисуем маркер на линии 
			imshow("Line2Debug", line);             //выводим изображение
		}


		return min;

	}

	void MyFilledCircle(Mat img, Point center)
	{
		circle(img,
			center,
			10,                  //радиус круга
			Scalar(0, 255, 0),   //цвет круга
			FILLED,
			LINE_8);
	}
}
