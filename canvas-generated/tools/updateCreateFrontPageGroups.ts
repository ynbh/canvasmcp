
import { tool } from "ai";
import { updateCreateFrontPageGroupsDataSchema } from "./aitm.schema.ts";
import { updateCreateFrontPageGroups, UpdateCreateFrontPageGroupsData } from "..";

export default tool({
  description: `
  Update/create front page
Update the title or contents of the front page
    `,
  parameters: updateCreateFrontPageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCreateFrontPageGroupsData, "url"> ) => {
    try {
      const { data } = await updateCreateFrontPageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    