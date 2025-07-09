
import { tool } from "ai";
import { getAllUsersInGroupLtiDataSchema } from "./aitm.schema.ts";
import { getAllUsersInGroupLti, GetAllUsersInGroupLtiData } from "..";

export default tool({
  description: `
  Get all users in a group (lti)
Get all Canvas users in a group. Tool providers may only
access
groups that belong to the context the tool is installed in.
    `,
  parameters: getAllUsersInGroupLtiDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetAllUsersInGroupLtiData, "url"> ) => {
    try {
      const { data } = await getAllUsersInGroupLti(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    