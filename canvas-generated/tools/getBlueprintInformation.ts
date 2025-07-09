
import { tool } from "ai";
import { getBlueprintInformationDataSchema } from "./aitm.schema.ts";
import { getBlueprintInformation, GetBlueprintInformationData } from "..";

export default tool({
  description: `
  Get blueprint information
Using 'default' as the template_id should suffice for the current
implmentation (as there should be only one template per course).
However, using specific template
ids may become necessary in the future
    `,
  parameters: getBlueprintInformationDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetBlueprintInformationData, "url"> ) => {
    try {
      const { data } = await getBlueprintInformation(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    