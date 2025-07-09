
import { tool } from "ai";
import { listAvatarOptionsDataSchema } from "./aitm.schema.ts";
import { listAvatarOptions, ListAvatarOptionsData } from "..";

export default tool({
  description: `
  List avatar options
A paginated list of the possible user avatar options that can be set with the
user update endpoint. The response will be an array of avatar records. If the 'type' field is
'attachment', the record will include all the normal attachment json fields; otherwise it will
include only the 'url' and 'display_name' fields. Additionally, all records will include a 'type'
field and a 'token' field. The following explains each field in more detail
type::
["gravatar"|"attachment"|"no_pic"] The type of avatar record, for categorization purposes.
url:: The
url of the avatar
token:: A unique representation of the avatar record which can be used to set the
avatar with the user update endpoint. Note: this is an internal representation and is subject to
change without notice. It should be consumed with this api endpoint and used in the user update
endpoint, and should not be constructed by the client.
display_name:: A textual description of the
avatar record
id:: ['attachment' type only] the internal id of the attachment
content-type::
['attachment' type only] the content-type of the attachment
filename:: ['attachment' type only] the
filename of the attachment
size:: ['attachment' type only] the size of the attachment
    `,
  parameters: listAvatarOptionsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ListAvatarOptionsData, "url"> ) => {
    try {
      const { data } = await listAvatarOptions(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    