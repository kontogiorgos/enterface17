//
//  main.cpp
//  Openface server
//
//  Created by Patrik Jonell on 2017-07-15.
//  Copyright © 2017 Patrik Jonell. All rights reserved.
//

#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include "LandmarkCoreIncludes.h"
#include "FaceAnalyser.h"
#include <vector>
#include <zmq.hpp>
#include <iostream>
#include <SimpleAmqpClient/SimpleAmqpClient.h>
#include <msgpack.hpp>
#include "json.hpp"
#include <time.h>

using json = nlohmann::json;

std::vector<std::string> get_arguments(int argc, char **argv) {
   std::vector<std::string> arguments;
   for(int i = 0; i < argc; ++i) {
       arguments.push_back(std::string(argv[i]));
   }
   return arguments;
}

int main(int argc, char * argv[]) {
    std::vector<std::string> arguments = get_arguments(argc, argv);
    if(arguments.size() != 2) {
        std::cout << "Error. facial_features [color]" << "\n";
        exit(EXIT_FAILURE);
    }

    AmqpClient::Channel::ptr_t channel = AmqpClient::Channel::Create("192.168.0.108", 5672, "test", "test");
    channel->DeclareExchange("sensors", "topic");
    std::string queue = channel->DeclareQueue("openface-queue2");
    channel->BindQueue(queue, "sensors", "video.new_sensor." + arguments[1]);
    std::string consumer = channel->BasicConsume(queue);
    AmqpClient::Envelope::ptr_t env = channel->BasicConsumeMessage();

    json j = json::parse(env->Message()->Body());


    LandmarkDetector::FaceModelParameters det_parameters;
    LandmarkDetector::CLNF clnf_model(det_parameters.model_location);
    int sim_size = 112;
    double sim_scale = sim_size * (0.7 / 112.0);
    std::string au_loc = "AU_predictors/AU_all_best.txt";
    std::string tri_loc = "model/tris_68_full.txt";

    FaceAnalysis::FaceAnalyser face_analyser(std::vector<cv::Vec3d>(), sim_scale, sim_size, sim_size, au_loc, tri_loc);
    int frame_count = 0;
    std::cout << "-" << j["address"] << "-\n";
    zmq::context_t context (1);
    zmq::socket_t s (context, ZMQ_SUB);
    s.connect (j["address"]);
    s.setsockopt(ZMQ_SUBSCRIBE, "", 0);

    std::cout << "Starting to listen for msgs\n";
    while (true) {
        zmq::message_t request;

        //  Wait for next request from client
        s.recv (&request);
        clock_t tStart = clock();

        msgpack::object_handle oh =
        msgpack::unpack(reinterpret_cast<char*>(request.data()), request.size());


        msgpack::object deserialized = oh.get();

        int imgHeight = j["img_size"]["height"];
        int imgWidth = j["img_size"]["width"];
        int imgFps = j["img_size"]["fps"];
        json results;

        std::tuple<std::string, double> msg;
        deserialized.convert(msg);

        char* chr = const_cast<char*>(std::get<0>(msg).c_str());
        cv::Mat cameraFrame = cv::Mat(imgHeight, imgWidth, CV_8UC3, chr);

        //cv::imshow("frame", img);
        //if( cv::waitKey(1) == 27 ) break;

        double fps = imgFps;
        cv::Mat greyMat;
        cv::Mat sim_warped_img;
        cv::cvtColor(cameraFrame, greyMat, cv::COLOR_BGR2GRAY);
        LandmarkDetector::DetectLandmarksInVideo(greyMat, clnf_model, det_parameters);
        double time_stamp = (double)frame_count * (1.0 / fps);

        face_analyser.AddNextFrame(greyMat, clnf_model, time_stamp, false, !det_parameters.quiet_mode);
        face_analyser.GetLatestAlignedFace(sim_warped_img);

        frame_count++;
        auto aus_reg = face_analyser.GetCurrentAUsReg();

        std::vector<std::string> au_reg_names = face_analyser.GetAURegNames();
        std::sort(au_reg_names.begin(), au_reg_names.end());

        std::vector<std::string> au_names_reg = face_analyser.GetAURegNames();
        std::vector<std::string> au_names_class = face_analyser.GetAUClassNames();

        // std::sort(au_names_reg.begin(), au_names_reg.end());
        // for (std::string reg_name : au_names_reg)
        // {
        //     results[reg_name + "_r"] = NULL;
        //     // cout << ", " << reg_name << "_r";
        // }

        // std::sort(au_names_class.begin(), au_names_class.end());
        // for (std::string class_name : au_names_class)
        // {
        //     results[class_name + "_c"] = NULL;
        //     // cout << ", " << class_name << "_c";
        // }


        // write out ar the correct index
        for (std::string au_name : au_reg_names)
        {
            for (auto au_reg : aus_reg)
            {
                results[au_reg.first + "_r"] = au_reg.second;
                // std::cout << au_reg.first << ": " << au_reg.second << "\n";
                // if (au_reg.second < 0) {
                //   val = 0.0;
                // }
                // if (au_reg.second >= 0) {
                //     // val = (au_reg.second/5)*2;
                //     // val = au_reg.second/2;
                // } else {
                //     // val = 0.0;
                // }

                // if (au_reg.second > 0.99) {
                //     cout << au_reg.second;
                //     cout << "\n";
                // }

                // if(au_reg.first.compare("AU01") == 0) {
                    // cout << "stuff" << "\n";
                    // setWeight(0, average(au01, count01, val));
                // }



                // if(au_reg.first.compare("AU45") == 0) {
                //     float f = average(au45, count45, val);
                //     cout << f;
                //     cout << "\n";
                //     setWeight(52, f);
                //     setWeight(53, f);
                // }

                // first++;
                // if (au_name.compare(au_reg.first) == 0)
                // {
                // 	// cout << ", " << au_reg.second;
                // 	break;
                // }
            }
        }



        // if (aus_reg.size() == 0)
        // {
        //     for (size_t p = 0; p < face_analyser.GetAURegNames().size(); ++p)
        //     {
        //
        //         // cout << ", 0";
        //     }
        // }

        auto aus_class = face_analyser.GetCurrentAUsClass();

        vector<string> au_class_names = face_analyser.GetAUClassNames();
        // std::sort(au_class_names.begin(), au_class_names.end());

        // write out ar the correct index
        for (string au_name : au_class_names)
        {
            for (auto au_class : aus_class)
            {
                results[au_class.first + "_c"] = au_class.second == 1;

                // if(au_class.first.compare("AU28") == 0) {
                //     setWeight(31, average(au28, count28, au_class.second));
                // }

                // if(au_class.first.compare("AU45") == 0) {
                //     float f = average(au45, count45, au_class.second);
                // }

                // if (au_name.compare(au_class.first) == 0)
                // {
                // 	// cout << ", " << au_class.second;
                // 	break;
                // }
            }
        }

        // if (aus_class.size() == 0)
        // {
        //     for (size_t p = 0; p < face_analyser.GetAUClassNames().size(); ++p)
        //     {
        //         // cout << ", 0";
        //     }
        // }


        cv::Vec6d pose_estimate;
        float cx = greyMat.cols / 2.0f;
        float cy = greyMat.rows / 2.0f;
        float fx = 500 * (greyMat.cols / 640.0);
        float fy = 500 * (greyMat.rows / 480.0);
        fx = (fx + fy) / 2.0;
        fy = fx;
        pose_estimate = LandmarkDetector::GetCorrectedPoseWorld(clnf_model, fx, fy, cx, cy);


        results["rot_x"] = pose_estimate[3];
        results["rot_y"] = pose_estimate[4];
        results["rot_z"] = pose_estimate[5];

        std::cout << std::get<1>(msg) + (double)(clock() - tStart)/CLOCKS_PER_SEC << "\n";
        json hello;
        hello["name"] = "openface-preprocessor";
        hello["arrived"] = std::get<1>(msg);
        hello["departed"] = std::get<1>(msg) + (double)(clock() - tStart)/CLOCKS_PER_SEC;

        results["timestamps"] = json::array({hello});

        // std::cout << "dat!" << "\n";
        channel->BasicPublish("pre-processor", "openface.data." + arguments[1], AmqpClient::BasicMessage::Create(results.dump()));
        cv::imshow("cam", sim_warped_img);
        cv::waitKey(1);
        // if (cv::waitKey(30) >= 0)
        //     break;

    }
    std::cout << "Hello, World!\n";
    return 0;
}
