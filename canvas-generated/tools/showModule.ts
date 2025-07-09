
import { tool } from "ai";
import { showModuleDataSchema } from "./aitm.schema.ts";
import { showModule, ShowModuleData } from "..";

export default tool({
  description: `
  Show module
Get information about a single module
    `,
  parameters: showModuleDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowModuleData, "url"> ) => {
    try {
      const { data } = await showModule(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    