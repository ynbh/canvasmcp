
import { tool } from "ai";
import { deletePageGroupsDataSchema } from "./aitm.schema.ts";
import { deletePageGroups, DeletePageGroupsData } from "..";

export default tool({
  description: `
  Delete page
Delete a wiki page
    `,
  parameters: deletePageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<DeletePageGroupsData, "url"> ) => {
    try {
      const { data } = await deletePageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    