
import { tool } from "ai";
import { updatePreferenceTypeDataSchema } from "./aitm.schema.ts";
import { updatePreferenceType, UpdatePreferenceTypeData } from "..";

export default tool({
  description: `
  Update a preference
Change the preference for a single notification for a single communication
channel
    `,
  parameters: updatePreferenceTypeDataSchema.omit({ url: true }),
  execute: async (args : Omit<UpdatePreferenceTypeData, "url"> ) => {
    try {
      const { data } = await updatePreferenceType(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    