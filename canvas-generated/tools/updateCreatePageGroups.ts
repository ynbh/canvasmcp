
import { tool } from "ai";
import { updateCreatePageGroupsDataSchema } from "./aitm.schema.ts";
import { updateCreatePageGroups, UpdateCreatePageGroupsData } from "..";

export default tool({
  description: `
  Update/create page
Update the title or contents of a wiki page
    `,
  parameters: updateCreatePageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCreatePageGroupsData, "url"> ) => {
    try {
      const { data } = await updateCreatePageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    