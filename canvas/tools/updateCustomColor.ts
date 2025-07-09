
import { tool } from "ai";
import { updateCustomColorDataSchema } from "./aitm.schema.ts";
import { updateCustomColor, UpdateCustomColorData } from "..";

export default tool({
  description: `
  Update custom color
Updates a custom color for a user for a given context.  This allows
colors for
the calendar and elsewhere to be customized on a user basis.

The asset string parameter should be
in the format 'context_id', for example
'course_42'
    `,
  parameters: updateCustomColorDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdateCustomColorData, "url"> ) => {
    try {
      const { data } = await updateCustomColor(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    