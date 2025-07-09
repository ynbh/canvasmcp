
import { tool } from "ai";
import { getModuleItemSequenceDataSchema } from "./aitm.schema.ts";
import { getModuleItemSequence, GetModuleItemSequenceData } from "..";

export default tool({
  description: `
  Get module item sequence
Given an asset in a course, find the ModuleItem it belongs to, the previous
and next Module Items
in the course sequence, and also any applicable mastery path rules
    `,
  parameters: getModuleItemSequenceDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetModuleItemSequenceData, "url"> ) => {
    try {
      const { data } = await getModuleItemSequence(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    