
import { tool } from "ai";
import { reLockModuleProgressionsDataSchema } from "./aitm.schema.ts";
import { reLockModuleProgressions, ReLockModuleProgressionsData } from "..";

export default tool({
  description: `
  Re-lock module progressions
Resets module progressions to their default locked state
and
recalculates them based on the current requirements.

Adding progression requirements to an
active course will not lock students
out of modules they have already unlocked unless this action is
called.
    `,
  parameters: reLockModuleProgressionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ReLockModuleProgressionsData, "url"> ) => {
    try {
      const { data } = await reLockModuleProgressions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    