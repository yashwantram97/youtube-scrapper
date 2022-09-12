import React, { useState } from "react";

import { Avatar, Comment } from "antd";
import { Modal } from "antd";

const CommentsModal = (props: any) => {
  const CommentElement = (props: any) => (
    <Comment
      actions={[<span>Likes: {props.likes}</span>]}
      author={<a>{props.author}</a>}
      avatar={
        <Avatar src="https://joeschmoe.io/api/v1/random" alt="Han Solo" />
      }
      content={<p>{props.content}</p>}
      datetime={<span>{new Date(props.dateCreated).toDateString()}</span>}
    >
      {props.children}
    </Comment>
  );
  const commentArr = props.commentsData.map((comment: any) => {
    if (props.commentsData.length === 0) {
      return <h1>Comment scrap in progress try after sometime.</h1>;
    }
    const mainComment = (reply: any) => (
      <CommentElement
        key={comment.comment_id}
        children={reply}
        author={comment.author}
        content={comment.comment_text}
        dateCreated={comment.created_at}
        likes={comment.comment_likes}
      />
    );
    if (comment.replies.length === 0) return mainComment([]);
    else {
      const replyComment = comment.replies.map((reply: any) => {
        return (
          <CommentElement
            key={reply.id}
            children={undefined}
            author={reply.authorDisplayName}
            content={reply.replyText}
            dateCreated={reply.created_at}
            likes={reply.likeCount}
          />
        );
      });
      return mainComment(replyComment);
    }
  });

  return (
    <>
      <Modal
        title="Comments"
        footer=""
        centered
        width={1000}
        open={props.open}
        onCancel={props.handleOkCancel}
      >
        {commentArr.length === 0
          ? "Please try again after sometime"
          : commentArr}
      </Modal>
    </>
  );
};

export default CommentsModal;
