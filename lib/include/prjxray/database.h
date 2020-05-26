/*
 * Copyright (C) 2017-2020  The Project X-Ray Authors.
 *
 * Use of this source code is governed by a ISC-style
 * license that can be found in the LICENSE file or at
 * https://opensource.org/licenses/ISC
 *
 * SPDX-License-Identifier: ISC
 */
#ifndef PRJXRAY_LIB_DATABASE_H
#define PRJXRAY_LIB_DATABASE_H

#include <memory>
#include <string>
#include <vector>

#include <prjxray/segbits_file_reader.h>

namespace prjxray {

class Database {
       public:
	Database(const std::string& path) : db_path_(path) {}

	std::vector<std::unique_ptr<SegbitsFileReader>> segbits() const;

       private:
	std::string db_path_;
};

}  // namespace prjxray

#endif  // PRJXRAY_LIB_DATABASE_H
