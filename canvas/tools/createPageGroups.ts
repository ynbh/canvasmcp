
import { tool } from "ai";
import { createPageGroupsDataSchema } from "./aitm.schema.ts";
import { createPageGroups, CreatePageGroupsData } from "..";

export default tool({
  description: `
  Create page
Create a new wiki page
    `,
  parameters: createPageGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreatePageGroupsData, "url"> ) => {
    try {
      const { data } = await createPageGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    