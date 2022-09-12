import React, { useState } from "react";

import { Route, Routes, Navigate } from "react-router-dom";
import { useNavigate } from "react-router";

import YTSHomepage from "./Components/YTSHomepage";
import ChannelSearch from "./Components/ChannelSearch";
import { Spin } from "antd";
import "antd/dist/antd.css";
import "./App.css";

function App(props: any) {
  const [showSpinner, setShowSpinner] = useState(false);
  const [scrapId, setScrapId] = useState();
  const navigate = useNavigate();

  const searchYTS = async (data: any) => {
    setShowSpinner(true)
    const response = await fetch(`http://localhost:80/api/scrap`, {
      method: "POST",
      headers: {
        Accept: "application/json",
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        channelName: data.channnelName,
        videoCount: Number(data.videoCount),
      }),
    });
    if (response.status !== 200) throw Error(data.message);
    const resData = await response.json();
    if (resData.status === true) {
      setScrapId(resData.id);
      navigate(`/ytssearchResults/${resData.id}`, { replace: true });
    }
    setShowSpinner(false);
  };

  return (
    <div className="App">
      <Spin tip="Loading..." spinning={showSpinner}>
        <Routes>
          <Route path="/" element={<Navigate to="/ytshomepage" />} />
          <Route
            path="/ytshomepage"
            element={<YTSHomepage searchYTS={searchYTS} />}
          />
          <Route path="/ytssearchResults/:id" element={<ChannelSearch />} />
        </Routes>
      </Spin>
    </div>
  );
}

export default App;
