
import { tool } from "ai";
import { getPublicInlinePreviewUrlDataSchema } from "./aitm.schema.ts";
import { getPublicInlinePreviewUrl, GetPublicInlinePreviewUrlData } from "..";

export default tool({
  description: `
  Get public inline preview url
Determine the URL that should be used for inline preview of the file.
    `,
  parameters: getPublicInlinePreviewUrlDataSchema.omit({ url: true }),
  execute: async (args : Omit<GetPublicInlinePreviewUrlData, "url"> ) => {
    try {
      const { data } = await getPublicInlinePreviewUrl(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    