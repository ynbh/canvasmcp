
import { tool } from "ai";
import { selectMasteryPathDataSchema } from "./aitm.schema.ts";
import { selectMasteryPath, SelectMasteryPathData } from "..";

export default tool({
  description: `
  Select a mastery path
Select a mastery path when module item includes several possible
paths.
Requires Mastery Paths feature to be enabled.  Returns a compound document
with the
assignments included in the given path and any module items
related to those assignments
    `,
  parameters: selectMasteryPathDataSchema.omit({ url: true }),
  execute: async (args : Omit<SelectMasteryPathData, "url"> ) => {
    try {
      const { data } = await selectMasteryPath(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    