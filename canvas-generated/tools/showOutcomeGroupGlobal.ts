
import { tool } from "ai";
import { showOutcomeGroupGlobalDataSchema } from "./aitm.schema.ts";
import { showOutcomeGroupGlobal, ShowOutcomeGroupGlobalData } from "..";

export default tool({
  description: `
  Show an outcome group
    `,
  parameters: showOutcomeGroupGlobalDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowOutcomeGroupGlobalData, "url"> ) => {
    try {
      const { data } = await showOutcomeGroupGlobal(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    