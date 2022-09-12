import React from "react";
import "./buttonComponent.scss";

const ButtonComponent = (props: any) => {
  return (
    <React.Fragment>
      <button className="button-style" {...props}>
        {props.name.charAt(0).toUpperCase() + props.name.slice(1)}
      </button>
    </React.Fragment>
  );
};

export default ButtonComponent;
