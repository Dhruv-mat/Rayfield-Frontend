import React from "react";
import { Button } from "../../components/ui/button";
import { Card, CardContent } from "../../components/ui/card";
import { Input } from "../../components/ui/input";

export const LoginPage = (): JSX.Element => {
  return (
    <div className="bg-[#212121] flex flex-row justify-center w-full min-h-screen">
      <div className="bg-[#212121] overflow-hidden w-full max-w-[1440px] h-[1024px] relative">
        {/* Logo and Title */}
        <div className="absolute top-[97px] left-1/2 -translate-x-1/2 flex flex-col items-center gap-4">
          <div className="w-[53px] h-[53px] bg-[url(/union.svg)] bg-[100%_100%]" />
          <h1 className="font-outfit font-bold text-[#fff8f8] text-[40px]">
            Rayfield Systems
          </h1>
        </div>

        {/* Login Card and Background Effect */}
        <div className="absolute w-full max-w-[1238px] h-[878px] top-[294px] left-1/2 -translate-x-1/4">
          {/* Green glow effect */}
          <div className="absolute w-[593px] h-[593px] top-[285px] left-[645px] bg-[#629a44] rounded-[296.5px] blur-[243.05px]" />

          {/* Login Card */}
          <Card className="absolute w-[705px] h-[508px] top-0 left-0 bg-[#1f1f1f] rounded-[35px] shadow-[0px_4px_16.1px_#00000040] opacity-[0.59] border-none">
            <CardContent className="p-0">
              <h2 className="absolute top-[26px] left-[91px] font-outfit font-medium text-white text-[40px]">
                Login
              </h2>

              {/* Email Input */}
              <div className="absolute w-[542px] h-[68px] top-[104px] left-[91px]">
                <div className="relative w-[540px] h-[68px] rounded-2xl">
                  <Input
                    className="absolute w-[540px] h-[68px] top-0 left-0 bg-[#484848] rounded-2xl shadow-[0px_4px_4px_#00000040] opacity-[0.44] text-white text-2xl px-5 py-4 border-none"
                    placeholder="EMAIL"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div className="absolute w-[542px] h-[68px] top-[191px] left-[91px]">
                <div className="relative w-[540px] h-[68px] rounded-2xl">
                  <Input
                    type="password"
                    className="absolute w-[540px] h-[68px] top-0 left-0 bg-[#484848] rounded-2xl shadow-[0px_4px_4px_#00000040] opacity-[0.44] text-white text-2xl px-5 py-4 border-none"
                    placeholder="PASSWORD"
                  />
                </div>
              </div>

              {/* Login Button and CSV Upload Link */}
              <div className="absolute w-[544px] h-[120px] top-[343px] left-[91px]">
                <Button className="absolute w-[540px] h-[68px] top-0 left-0 bg-[#629a44] rounded-2xl shadow-[0px_4px_4px_#00000040] opacity-[0.44] hover:opacity-[0.6] hover:bg-[#629a44] text-white text-[32px] font-normal font-inter">
                  Login
                </Button>

                <button className="absolute top-24 left-[136px] font-inter font-normal text-[#7d7d7d] text-xl tracking-[0] leading-[normal] whitespace-nowrap hover:text-white transition-colors">
                  Upload CSV Without Login
                </button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};
