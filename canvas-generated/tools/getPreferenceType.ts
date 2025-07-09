
import { tool } from "ai";
import { getPreferenceTypeDataSchema } from "./aitm.schema.ts";
import { getPreferenceType, GetPreferenceTypeData } from "..";

export default tool({
  description: `
  Get a preference
Fetch the preference for the given notification for the given communicaiton channel
    `,
  parameters: getPreferenceTypeDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetPreferenceTypeData, "url"> ) => {
    try {
      const { data } = await getPreferenceType(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    