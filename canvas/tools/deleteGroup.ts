
import { tool } from "ai";
import { deleteGroupDataSchema } from "./aitm.schema.ts";
import { deleteGroup, DeleteGroupData } from "..";

export default tool({
  description: `
  Delete a group
Deletes a group and removes all members.
    `,
  parameters: deleteGroupDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeleteGroupData, "url"> ) => {
    try {
      const { data } = await deleteGroup(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    