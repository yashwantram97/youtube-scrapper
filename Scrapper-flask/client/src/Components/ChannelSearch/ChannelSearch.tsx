import React, { useEffect, useState } from "react";
import { tableHeadings } from "../../consts/channelSearchConst";
import { Table, Spin } from "antd";
import CommentsModal from "./CommentsModal";
import { useParams,useNavigate } from "react-router-dom";
import "./channelSearch.scss";

const ChannelSearch = (props: any) => {
  const navigate = useNavigate();
  const [openComments, setOpenComments] = useState(false);
  const [commentsData, setCommentsData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [showSpinner, setShowSpinner] = useState(false);
  const { id } = useParams();

  const preload = async () => {
    setShowSpinner(true);
    const searchResponse = await fetch(
      `http://localhost:80/fetch/video_details?channel_id=${id}`
    );
    if (searchResponse.status !== 200) throw Error("No results found");
    const searchResData = await searchResponse.json();
    if (searchResData.status === true) {
      setTableData(searchResData.data);
    }
    setShowSpinner(false);
  };

  useEffect(() => {
    preload();
  }, []);

  const tableColumns = tableHeadings.map((heading: string) => {
    const headingText = heading.toLowerCase();
    let headingObj = {
      title: heading,
      dataIndex: headingText,
      key: headingText,
    };
    if (heading === "Thumbnail") headingObj.dataIndex = "thumbnail_url";

    if (heading === "Comments") headingObj.dataIndex = "id";

    switch (heading) {
      case "Thumbnail":
        Object.assign(headingObj, {
          render: (text: string) => <img src={text} alt={text} />,
        });
        break;
      case "Published_date":
        Object.assign(headingObj, {
          render: (text: string) => (
            <span>{new Date(text).toDateString()} </span>
          ),
        });
        break;
      case "Comments":
        Object.assign(headingObj, {
          render: (text: string) => (
            <a onClick={() => openCommentsModal(text)}>COMMENT LINK</a>
          ),
        });
        break;
      case "Video_link":
        Object.assign(headingObj, {
          render: (text: string) => (
            <a href={text} target="_blank">
              VIDEO LINK
            </a>
          ),
        });
        break;

      case "Video_status":
        Object.assign(headingObj, {
          render: (text: string | Number, record: any) => (
            <span>
              {text === 0 ? (
                "video download in queue"
              ) : text === -1 ? (
                <button
                  onClick={() =>
                    downloadVideoToS3(record.id, record.video_link)
                  }
                >
                  get video
                </button>
              ) : (
                <button onClick={() => downloadVideo(record.id)}>
                  download video
                </button>
              )}
            </span>
          ),
        });
        break;
    }
    return headingObj;
  });

  const downloadVideoToS3 = async (id: any, link: any) => {
    const response = await fetch(
      `http://localhost:80/queue/scrap/video`,
      {
        method: "POST",
        headers: {
          Accept: "application/json",
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id: id,
          link: link,
        }),
      }
    );
  };

  const downloadVideo = async (id: any) => {
    setShowSpinner(true);
    const response = await fetch(
      `http://localhost:80/queue/data?data=youtube&id=${id}`
    );
    if (response.ok) {
      const resData = await response.json();
      window.open(resData.data, '_blank', 'noopener,noreferrer');
    }
  };

  const openCommentsModal = async (id: any) => {
    setShowSpinner(true);
    const response = await fetch(
      `http://localhost:80/queue/data?data=comment&id=${id}`
    );
    if (response.ok) {
      const resData = await response.json();
      setCommentsData(resData.data);
      setOpenComments(true);
      setShowSpinner(false);
    }
  };

  const closeCommentsModal = () => {
    setCommentsData([]);
    setOpenComments(false);
  };

  return (
    <React.Fragment>
      <Spin tip="Loading..." spinning={showSpinner}>
        <div className="channelSearchContainer">
          <div className="channelSearchTable">
            <Table
              columns={tableColumns}
              dataSource={tableData}
              pagination={false}
              bordered
              title={() => (
                <div className="search-table-title-block">
                  <div>
                    <button
                      onClick={() => {
                        window.location.href =
                          "http://localhost:3000/ytshomepage";
                      }}
                    >
                      ◀BACK
                    </button>
                  </div>
                  <div className="search-table-title">
                    Channel search results
                  </div>
                  <div></div>
                </div>
              )}
            />
          </div>
          <CommentsModal
            open={openComments}
            handleOkCancel={closeCommentsModal}
            commentsData={commentsData}
          />
        </div>
      </Spin>
    </React.Fragment>
  );
};
export default ChannelSearch;
