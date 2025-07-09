
import { tool } from "ai";
import { postReplyGroupsDataSchema } from "./aitm.schema.ts";
import { postReplyGroups, PostReplyGroupsData } from "..";

export default tool({
  description: `
  Post a reply
Add a reply to an entry in a discussion topic. Returns a json
representation of the
created reply (see documentation for 'replies'
method) on success.

May require (depending on the
topic) that the user has posted in the topic.
If it is required, and the user has not posted, will
respond with a 403
Forbidden status and the body 'require_initial_post'.
    `,
  parameters: postReplyGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<PostReplyGroupsData, "url"> ) => {
    try {
      const { data } = await postReplyGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    