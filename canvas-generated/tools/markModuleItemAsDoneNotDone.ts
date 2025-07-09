
import { tool } from "ai";
import { markModuleItemAsDoneNotDoneDataSchema } from "./aitm.schema.ts";
import { markModuleItemAsDoneNotDone, MarkModuleItemAsDoneNotDoneData } from "..";

export default tool({
  description: `
  Mark module item as done/not done
Mark a module item as done/not done. Use HTTP method PUT to mark
as done,
and DELETE to mark as not done.
    `,
  parameters: markModuleItemAsDoneNotDoneDataSchema.omit({ url: true }),
  execute: async (args : Omit<MarkModuleItemAsDoneNotDoneData, "url"> ) => {
    try {
      const { data } = await markModuleItemAsDoneNotDone(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    