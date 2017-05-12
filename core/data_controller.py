"""
A sqlite3 database handler
"""


def get_prefix(cursor, server_id: str):
    """
    Get the server prefix from databse
    :param cursor: the database cursor
    :param server_id: the server id
    :return: the server prefix if found else none
    """
    sql = '''SELECT prefix FROM prefix WHERE server=?'''
    res = cursor.execute(sql, [server_id]).fetchone()
    return res[0] if res is not None else None


def set_prefix(connection, cursor, server_id: str, prefix: str):
    """
    Set the prefix for a server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param prefix: the command prefix
    """
    sql_replace = '''REPLACE INTO prefix VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, prefix))
    connection.commit()


def delete_prefix(connection, cursor, server_id: str):
    """
    Delete the prefix for a server
    :param connection: the db connection
    :param cursor: the db cursor
    :param server_id: the server id
    """
    sql_delete = '''
    DELETE FROM prefix WHERE server=?
    '''
    cursor.execute(sql_delete, [server_id])
    connection.commit()


def write_tag(connection, cursor, site, tag):
    """
    Write a tag entry into the database
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param site: the site name
    :param tag: the tag entry
    """
    sql_replace = '''REPLACE INTO nsfw_tags VALUES (?, ?)'''
    cursor.execute(sql_replace, (site, tag))
    connection.commit()


def write_tag_list(connection, cursor, site, tags):
    """
    Writes a list of tags into the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param site: the site name
    :param tags: the list of tags
    """
    for tag in tags:
        write_tag(connection, cursor, site, tag)


def tag_in_db(cursor, site, tag):
    """
    Returns if the tag is in the db or not
    :param cursor: the database cursor
    :param site: the site name
    :param tag: the tag name
    :return: True if the tag is in the db else false
    """
    sql = '''
    SELECT EXISTS(SELECT 1 FROM nsfw_tags WHERE site=? AND tag=?LIMIT 1)
    '''
    cursor.execute(sql, (site, tag))
    return cursor.fetchone() == (1,)


def fuzzy_match_tag(cursor, site, tag):
    """
    Try to fuzzy match a tag with one in the db
    :param cursor: the database cursor
    :param site: the stie name
    :param tag: the tag name
    :return: a tag in the db if match success else None
    """
    sql = """
    SELECT tag FROM nsfw_tags 
    WHERE (tag LIKE '{0}%' OR tag LIKE '%{0}%' OR tag LIKE '%{0}') 
    AND site=?
    """.format(tag)
    res = cursor.execute(sql, [site]).fetchone()
    return res[0] if res is not None else None


def get_language(cursor, server_id: str):
    """
    Get the server language from databse
    :param cursor: the database cursor
    :param server_id: the server id
    :return: the server language if found else none
    """
    sql = '''SELECT lan FROM language WHERE server=?'''
    res = cursor.execute(sql, [server_id]).fetchone()
    return res[0] if res is not None else None


def set_language(connection, cursor, server_id: str, language: str):
    """
    Set the language for a server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param language: the language
    """
    sql_replace = '''REPLACE INTO language VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, language))
    connection.commit()


def delete_language(connection, cursor, server_id: str):
    """
    Delete the language info for a server
    :param connection: the db connection
    :param cursor: the db cursor
    :param server_id: the server id
    """
    sql_delete = '''
    DELETE FROM language WHERE server=?
    '''
    cursor.execute(sql_delete, [server_id])
    connection.commit()


def add_role(connection, cursor, server_id: str, role: str):
    """
    Add a role to the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param role: the role name
    """
    sql_replace = '''REPLACE INTO roles VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, role))
    connection.commit()


def remove_role(connection, cursor, server_id: str, role: str):
    """
    Remove a role from the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id 
    :param role: the role name
    """
    sql = '''
    DELETE FROM roles WHERE server=? AND role=?
    '''
    cursor.execute(sql, [server_id, role])
    connection.commit()


def get_role_list(cursor, server_id: str):
    """
    Get the list of roles under the server with id == server_id
    :param cursor: the database cursor
    :param server_id: the server 
    :return: a list of roles under the server with id == server_id
    """
    sql = '''
    SELECT role FROM roles WHERE server=?
    '''
    cursor.execute(sql, [server_id])
    return [i[0] for i in cursor.fetchall()]


def set_mod_log(connection, cursor, server_id: str, channel_id: str):
    """
    Set the mod log channel id for a given server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param channel_id: the channel id
    """
    sql_replace = '''REPLACE INTO mod_log VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, channel_id))
    connection.commit()


def get_mod_log(cursor, server_id: str):
    """
    Get a list of all mod logs from a given server
    :param cursor: the database cursor
    :param server_id: the server id
    :return: a list of all mod log channel ids
    """

    sql = '''
    SELECT channel FROM mod_log WHERE server=?
    '''
    cursor.execute(sql, [server_id])
    return [i[0] for i in cursor.fetchall()]


def remove_mod_log(connection, cursor, server_id: str, channel_id: str):
    """
    Delete a modlog from the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param channel_id: the channel id
    """
    sql = '''
    DELETE FROM mod_log WHERE server=? AND channel=?
    '''
    cursor.execute(sql, [server_id, channel_id])
    connection.commit()


def add_warn(connection, cursor, server_id: str, user_id: str):
    """
    Add 1 to the warning count of the user
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    """
    sql_insert = '''INSERT OR IGNORE INTO warns VALUES(?,?,0)'''
    sql = '''
    UPDATE warns SET number = number + 1 WHERE server = ? AND user = ?
    '''
    cursor.execute(sql_insert, [server_id, user_id])
    cursor.execute(sql, [server_id, user_id])
    connection.commit()


def remove_warn(connection, cursor, server_id: str, user_id: str):
    """
    Subtract 1 from the warning count of the user
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    """
    sql = '''
    UPDATE warns SET number = number - 1 
    WHERE server = ? AND user = ? AND number > 0
    '''
    cursor.execute(sql, [server_id, user_id])
    connection.commit()


def get_warn(cursor, server_id: str, user_id: str):
    """
    Get the warning count of a user
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    :return: the warning count of the user
    """
    sql = '''
    SELECT number FROM warns WHERE server = ? AND user = ?
    '''
    cursor.execute(sql, [server_id, user_id])
    result = cursor.fetchone()
    return result[0] if result is not None else 0
