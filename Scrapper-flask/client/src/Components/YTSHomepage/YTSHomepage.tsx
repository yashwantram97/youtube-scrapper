import React from "react";

import { useForm } from "react-hook-form";
import Button from "../UI-Elements/ButtonComponent/ButtonComponent";
import "./yTSHomepage.scss";

const YTSHomepage = (props: any) => {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm();

  const onSubmit = (data: any) => {
    props.searchYTS(data);
  };
  return (
    <React.Fragment>
      <div className="yTSHomePageContainer">
        <div className="searchformContainer">
          <h1>Youtube Scrapper Project</h1>
          <form onSubmit={handleSubmit(onSubmit)}>
            <div>
              <label htmlFor="channnelName">Channel Name (ex: krishnaik06)</label> <br />
              <input
                type="text"
                className="form-control"
                id="channnelName"
                autoComplete="off"
                placeholder="Enter Channel Name"
                {...register("channnelName", {
                  required: true,
                })}
              />
            </div>
            <div>
              <label htmlFor="videoCount">Video Count</label> <br />
              <input
                type="number"
                max={50}
                className="form-control"
                id="videoCount"
                autoComplete="off"
                placeholder="Enter Video Count"
                {...register("videoCount", {
                  required: true,
                })}
              />
            </div>
            <div>
              <Button name="submit" type="submit" />
              <Button name="reset" type="reset" />
            </div>
          </form>
        </div>
      </div>
    </React.Fragment>
  );
};
export default YTSHomepage;
